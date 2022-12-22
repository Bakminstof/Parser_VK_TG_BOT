import logging.config

from copy import deepcopy
from typing import List, Dict
from sqlalchemy import select, update
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext
from sqlalchemy.dialects.postgresql import insert

from db import async_mian_session, GroupsTable
from loader import dp
from states import States
from data.prices import BASE_SLOTS_COUNT
from utils.logging import dict_config
from hendlers.handlers_funcs import update_groups_count, check_group
from keyboards.inline.callbacks import callback_channels, callback_choice
from keyboards.inline import (
    channels_add_keyboard,
    channels_choice_keyboard,
    channels_change_del_back_keyboard,
    channels_add_group_slot_keyboard
)

logging.config.dictConfig(dict_config)
edit_rls_logger = logging.getLogger('edit_rls')

CMD = 'channels'


# Просмотр связей для изменения
@dp.callback_query_handler(
    callback_choice.filter(choice='no'), state=[
        States.DelEmptySlotState,
        States.DelOccupiedSlotState
    ]
)
@dp.callback_query_handler(callback_channels.filter(type='back'), state=States.DelOccupiedSlotState)
@dp.callback_query_handler(callback_choice.filter(choice='no'), state=States.AcceptChangeState)
@dp.callback_query_handler(callback_channels.filter(type='back'), state=States.EditRlsState)
@dp.callback_query_handler(callback_channels.filter(type='edit'), state=None)
async def edit_group(call: CallbackQuery, state: FSMContext):
    id_user = call.from_user.id

    async with state.proxy() as data:
        if data.get('current_slot_type'):
            del data['current_slot_type']

        rls: Dict[int, Dict[str, str | int | List[int]]] = data.get('rls')

        additionally_search_group = data.get(id_user).get('additionally_search_group', 0)
        additionally_send_group = data.get(id_user).get('additionally_send_group', 0)

        current_main_count = data.get('current_main_count')
        current_send_to_count = data.get('current_send_to_count')

    max_main_count = BASE_SLOTS_COUNT + additionally_search_group
    max_send_to_count = BASE_SLOTS_COUNT + additionally_send_group

    relationships = []
    rls_dict = {}
    index = 1

    for row in rls.values():
        rls_dict[index] = row.get('id')
        relationships.append(
            '<b>~ /{index} {main_name} ==> {send_to_name}</b>'.format(
                index=index,
                main_name=row.get('main_group_name'),
                send_to_name=row.get('send_to_group_name')
            )
        )

        index += 1

    msg = '<b>Слоты для сбора информации:\nтекущие - {current_main}, максимум - {max_main}\n\n' \
          'Слоты для отправки информации:\nтекущие - {current_send_to}, максимум - {max_send_to}\n\n' \
          'Связи для редактирования:</b>\n\n{rls_}'.format(
            current_main=current_main_count,
            max_main=max_main_count,
            current_send_to=current_send_to_count,
            max_send_to=max_send_to_count,
            rls_='\n\n'.join(relationships)
          ) \
        if relationships \
        else '<b>Вам нечего редактировать. Добавьте каналы</b>'

    await call.message.edit_text(msg, parse_mode='HTML', reply_markup=channels_add_keyboard)

    await States.EditRlsState.set()

    async with state.proxy() as data:
        data['rls_indexes'] = rls_dict

    edit_rls_logger.info('User `{id_user}`: start edit rls'.format(id_user=id_user))


# Изменение конкретной связи
@dp.message_handler(state=States.EditRlsState)
async def edit_current_rls(message: Message, state: FSMContext):
    try:
        com = int(message.text[1:])

        async with state.proxy() as data:
            rls_dict = data.get('rls_indexes')
            rls_item = data.get('rls').get(rls_dict.get(com))

            if rls_item:
                if com in rls_dict.keys():
                    msg = '<b>~ {main_name}</b>' \
                          ' \u27a1\ufe0f ' \
                          '<b>{send_to_name}</b>\n\n'.format(
                            main_name=rls_item.get('main_group_name'),
                            send_to_name=rls_item.get('send_to_group_name')
                          )

                    await message.answer(msg, parse_mode='HTML', reply_markup=channels_change_del_back_keyboard)

                    edit_rls_logger.info(
                        'User `{id_user}`: edit current rls :: {rls}'.format(id_user=message.from_user.id, rls=msg)
                    )

                    data['current_rls'] = deepcopy(rls_item)

            else:
                await message.answer('Не понимаю :/')

    except Exception as ex:
        edit_rls_logger.exception('User `{id_user}`: exception {ex}'.format(id_user=message.from_user.id, ex=ex))

        await message.answer('Не понимаю :/')


# Промежуточный хэндлер для ссылки
@dp.callback_query_handler(callback_channels.filter(type='add'), state=States.EditRlsState)
@dp.callback_query_handler(callback_channels.filter(type='change'), state=States.EditRlsState)
async def edit_rls(call: CallbackQuery):
    msg = '<b>Вставьте ссылку на канал, с которого брать информацию</b>'

    await call.message.edit_text(msg, parse_mode='HTML')
    await States.AddMainGroupState.set()

    edit_rls_logger.info('User `{id_user}`: start add group url'.format(id_user=call.from_user.id, cmd=CMD))


# Удаление конкретной связи
@dp.callback_query_handler(callback_channels.filter(type='del'), state=States.EditRlsState)
async def del_rls(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        current_rls_id = data.get('current_rls').get('id')
        rls = data.get('current_rls')

        user_id = call.from_user.id

        group_stmt = select(GroupsTable.id, GroupsTable.user_ids).filter(current_rls_id == GroupsTable.id)

        check = await async_mian_session.execute(group_stmt)
        check = check.one_or_none()

        user_ids = set(check.user_ids)
        user_ids.remove(user_id)

        update_stmt = update(GroupsTable).where(GroupsTable.id == check.id).values(user_ids=user_ids)

        await async_mian_session.execute(update_stmt)
        await async_mian_session.commit()

        del data['rls'][current_rls_id]
        del data['current_rls']

        await update_groups_count(user_id, data)

        await call.message.edit_text('<b>Удалено!</b>', parse_mode='HTML')

        await state.reset_state(with_data=False)

        edit_rls_logger.info('User `{id_user}`: deleted rls :: {rls}'.format(id_user=call.from_user.id, rls=rls))


# Добавление групп для сбора и отправки
@dp.message_handler(state=[States.AddMainGroupState, States.AddSendToGroupState])
async def add_main_group(message: Message, state: FSMContext):
    mes = await message.answer('Секундочку...')
    id_user = message.from_user.id

    async with state.proxy() as data:
        search_groups_count = data.get('search_group_count', 0)
        send_groups_count = data.get('send_group_count', 0)

        additionally_search_group = data.get(id_user).get('additionally_search_group', 0)
        additionally_send_group = data.get(id_user).get('additionally_send_group', 0)

        main_groups_limit = BASE_SLOTS_COUNT + additionally_search_group
        send_to_groups_limit = BASE_SLOTS_COUNT + additionally_send_group

        current_mian_groups = search_groups_count
        current_send_groups = send_groups_count

        url = message.text.lower()

        group = await check_group(url)

        if group == 'Closed':
            await mes.edit_text('Закрытый канал. Выберите другой')

            edit_rls_logger.info(
                'User `{id_user}`: Closed channel :: {channel}'.format(id_user=id_user, channel=url)
            )

        elif group == 'Not found':
            await mes.edit_text('Канал не найден. Пожалуйста проверьте ссылку')

            edit_rls_logger.info(
                'User `{id_user}`: Not found channel :: {channel}'.format(id_user=id_user, channel=url)
            )

        elif group == 'Bad':
            await mes.edit_text(
                'Некорректная ссылка, пожалуйста вставьте ссылку формата:\n'
                '`https://t.me/...` или `https://vk.com/...`'
            )

            edit_rls_logger.info(
                'User `{id_user}`: Bad URL :: {channel}'.format(id_user=id_user, channel=url)
            )

        elif group == 'Cant see all posts':
            await mes.edit_text('В этой группе нельзя просмотреть все посты. Выберите другую группу')

            edit_rls_logger.info(
                'User `{id_user}`: Cant see all posts in channel :: {channel}'.format(id_user=id_user, channel=url)
            )

        else:
            state_name = await state.get_state()

            check_exist_current_rls = data.get('current_rls')

            if not check_exist_current_rls:
                data['current_rls'] = {}

            if state_name == States.AddSendToGroupState.state:
                send_to = data.get('rls').values()
                send_to_groups = [gr.get('send_to_group_url') for gr in send_to]

                current_send_to = True if group.get('url') in send_to_groups else False

                if current_send_groups == send_to_groups_limit and not current_send_to:
                    await mes.edit_text(
                        'У вас лимит по каналам для отправки',
                        reply_markup=channels_add_group_slot_keyboard
                    )
                    await state.reset_state(with_data=False)
                else:

                    data['current_rls']['send_to_group_name'] = group.get('name')
                    data['current_rls']['send_to_group_url'] = group.get('url')
                    data['current_rls']['send_to_group_type'] = group.get('type')
                    data['current_rls']['send_to_group_id'] = group.get('id')

                    rls_item = data.get('current_rls')

                    msg = '<b>~ {main_name}</b>' \
                          ' \u27a1\ufe0f ' \
                          '<b>{send_to_name}</b>\n\n'.format(
                            main_name=rls_item.get('main_group_name'),
                            send_to_name=rls_item.get('send_to_group_name')
                          )

                    await mes.edit_text(
                        '{}<b>Сохранить?</b>'.format(msg),
                        parse_mode='HTML',
                        reply_markup=channels_choice_keyboard
                    )

                    await States.AcceptChangeState.set()

                    edit_rls_logger.info(
                        'User `{id_user}`: Pre add send group :: {channel}'.format(id_user=id_user, channel=url)
                    )

            else:
                if group.get('user_name'):
                    await mes.edit_text('У пользователя нельзя получать информацию. Пожалуйста выберете канал')

                    edit_rls_logger.info(
                        'User `{id_user}`: User choice :: {channel}'.format(id_user=id_user, channel=url)
                    )

                else:
                    main = data.get('rls').values()
                    main_groups = [gr.get('main_group_url') for gr in main]

                    current_main = True if group.get('url') in main_groups else False

                    if current_mian_groups == main_groups_limit and not current_main:
                        await mes.edit_text(
                            'У вас лимит по каналам для сбора',
                            reply_markup=channels_add_group_slot_keyboard
                        )
                        await state.reset_state(with_data=False)
                    else:
                        data['current_rls']['main_group_name'] = group.get('name')
                        data['current_rls']['main_group_url'] = group.get('url')
                        data['current_rls']['main_group_type'] = group.get('type')
                        data['current_rls']['main_group_id'] = group.get('id')

                        await mes.edit_text('Готово! Теперь вставьте ссылку на канал, в который будем отправлять')
                        await States.AddSendToGroupState.set()

                        edit_rls_logger.info(
                            'User `{id_user}`: Pre add mian group :: {channel}'.format(id_user=id_user, channel=url)
                        )


# Изменение или добавление связей в базе данных
@dp.callback_query_handler(callback_choice.filter(choice='yes'), state=States.AcceptChangeState)
async def accept_data(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    async with state.proxy() as data:
        current_rls: Dict[str, str | int | List[int] | set[int]] = data.get('current_rls')
        current_rls_id = current_rls.get('id')

        check_exists_rls_stmt = select(GroupsTable.id, GroupsTable.user_ids) \
            .filter(GroupsTable.main_group_url == current_rls.get('main_group_url')) \
            .filter(GroupsTable.send_to_group_url == current_rls.get('send_to_group_url'))

        check_exists_rls = await async_mian_session.execute(check_exists_rls_stmt)
        check_exists_rls = check_exists_rls.one_or_none()

        if current_rls_id:  # Убираем id пользователя из его редактируемой связи
            group_stmt = select(GroupsTable.id, GroupsTable.user_ids).filter(current_rls_id == GroupsTable.id)

            check = await async_mian_session.execute(group_stmt)
            check = check.one_or_none()

            user_ids = set(check.user_ids)
            user_ids.remove(user_id)

            update_stmt = update(GroupsTable).where(GroupsTable.id == check.id).values(user_ids=user_ids)

            await async_mian_session.execute(update_stmt)
            await async_mian_session.commit()

            del data['rls'][current_rls_id]

        if check_exists_rls:  # Изменяем связь добавляя id пользователя, если она уже существует
            user_ids = set(check_exists_rls.user_ids)
            user_ids.add(user_id)

            check_id = current_rls.get('id')

            if check_id:
                del current_rls['id']

            current_rls['user_ids'] = user_ids

            update_stmt = update(GroupsTable).where(GroupsTable.id == check_exists_rls.id).values(**current_rls)

            await async_mian_session.execute(update_stmt)
            await async_mian_session.commit()

            current_rls['id'] = check_exists_rls.id
            data['rls'][check_exists_rls.id] = current_rls

        else:  # Добавляем связь
            current_rls['user_ids'] = [user_id]

            check_id = current_rls.get('id')

            if check_id:
                del current_rls['id']

            insert_stmt = insert(GroupsTable).values(**current_rls)

            await async_mian_session.execute(insert_stmt)
            await async_mian_session.commit()

            get_current_group_stmt = select(
                GroupsTable.id,
                GroupsTable.main_group_name,
                GroupsTable.main_group_url,
                GroupsTable.main_group_type,
                GroupsTable.main_group_id,
                GroupsTable.send_to_group_name,
                GroupsTable.send_to_group_url,
                GroupsTable.send_to_group_type,
                GroupsTable.send_to_group_id,
                GroupsTable.user_ids
            ). \
                filter(GroupsTable.main_group_name == current_rls.get('main_group_name')). \
                filter(GroupsTable.send_to_group_name == current_rls.get('send_to_group_name'))

            res = await async_mian_session.execute(get_current_group_stmt)

            current_group = res.one_or_none()
            group = {}

            for key in current_group.keys():
                group[key] = current_group[key]

            data['rls'][group.get('id')] = group

        del data['current_rls']

        await update_groups_count(user_id, data)

    await call.message.edit_text('Сохранено!', reply_markup=None)
    await state.reset_state(with_data=False)

    edit_rls_logger.info(
        'User `{id_user}`: Accept and save changes in DB:: {channel}'.format(id_user=user_id, channel=current_rls)
    )
