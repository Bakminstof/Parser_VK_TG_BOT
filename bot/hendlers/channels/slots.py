import logging.config

from typing import Tuple
from sqlalchemy import select
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from sqlalchemy.dialects.postgresql import insert

from db import async_session, GroupsTable, update_user_stmt
from states import States
from loader import dp
from data.prices import BASE_SLOTS_COUNT
from hendlers.handlers_funcs import build_slot_indexes
from keyboards.inline import (
    channels_choice_keyboard,
    channels_slot_type_keyboard,
    back_keyboard,
    slots_price_keyboard
)
from keyboards.inline.callbacks import (
    callback_choice,
    callback_slots,
    callback_slot_type
)
from utils.logging import dict_config

logging.config.dictConfig(dict_config)
slots_logger = logging.getLogger('slots')


# Слоты
@dp.callback_query_handler(callback_slots.filter(), state=[None, States.EditRlsState])
async def choice_slot_type(call: CallbackQuery):
    if call.data.split(':')[-1] == 'add_slot':
        await States.AddSlotState.set()
    elif call.data.split(':')[-1] == 'del_slot':
        await States.DelSlotState.set()

    await call.message.answer('Выберите тип слота', reply_markup=channels_slot_type_keyboard)

    slots_logger.info(
        'User `{id_user}`: Start edit additional slots'.format(id_user=call.from_user.id)
    )


# Выбор количества добавляемых слотов
@dp.callback_query_handler(callback_slot_type.filter(), state=States.AddSlotState)
async def add_slot_count(call: CallbackQuery):
    if call.data.split(':')[-1] == 'collect':
        await States.CollectSlotState.set()
    elif call.data.split(':')[-1] == 'send':
        await States.SendSlotState.set()

    msg = 'Сколько слотов добавить?\n' \
          'Слоты будут добавлены до конца текущей подписки ' \
          'по стоимости оставшихся дней подписки по месячному тарифу.\n' \
          'При дальнейшем продлении подписки будут учитываться добавленные слоты и стоимость будет скорректирована'

    await call.message.edit_text(msg, reply_markup=slots_price_keyboard)

    slots_logger.info(
        'User `{id_user}`: Choice slots count'.format(id_user=call.from_user.id)
    )


# Выбор слота для удаления
@dp.callback_query_handler(callback_slot_type.filter(), state=States.DelSlotState)
async def del_slot(call: CallbackQuery, state: FSMContext):
    id_user = call.from_user.id

    async with state.proxy() as data:
        additionally_search_group = data.get(id_user).get('additionally_search_group', 0)
        additionally_send_group = data.get(id_user).get('additionally_send_group', 0)

        current_main_count = data.get('current_main_count')
        current_send_to_count = data.get('current_send_to_count')

        if call.data.split(':')[-1] == 'collect' and additionally_search_group > 0:
            data['current_slot_type'] = 'collect'

            if BASE_SLOTS_COUNT + additionally_search_group == current_main_count:
                await States.DelOccupiedSlotState.set()

                main_groups: set[Tuple[str, str]] = data.get('main_groups')

                msg = await build_slot_indexes(main_groups, data)

                await call.message.edit_text(
                    msg,
                    reply_markup=back_keyboard,
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            else:
                await States.DelEmptySlotState.set()
                await call.message.edit_text('Удалить слот?', reply_markup=channels_choice_keyboard)

                slots_logger.info(
                    'User `{id_user}`: Choice to delete collect slot'.format(id_user=id_user)
                )

        elif call.data.split(':')[-1] == 'send' and additionally_send_group > 0:
            data['current_slot_type'] = 'send'

            if BASE_SLOTS_COUNT + additionally_send_group == current_send_to_count:
                await States.DelOccupiedSlotState.set()

                send_to_groups = data.get('send_to_groups')

                msg = await build_slot_indexes(send_to_groups, data)

                await call.message.edit_text(
                    msg,
                    reply_markup=back_keyboard,
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            else:
                await States.DelEmptySlotState.set()
                await call.message.edit_text('Удалить слот?', reply_markup=channels_choice_keyboard)

                slots_logger.info(
                    'User `{id_user}`: Choice to delete send slot'.format(id_user=id_user)
                )

        elif call.data.split(':')[-1] == 'collect' and additionally_search_group == 0:
            await call.message.edit_text(
                'У вас нет дополнительных слотов для сбора, вы не можете удалять базовые слоты'
            )
            await state.reset_state(with_data=False)

            slots_logger.info(
                'User `{id_user}`: Dont have additional collect slots'.format(id_user=call.from_user.id)
            )

        elif call.data.split(':')[-1] == 'send' and additionally_send_group == 0:
            await call.message.edit_text(
                'У вас нет дополнительных слотов для отправки, вы не можете удалять базовые слоты'
            )
            await state.reset_state(with_data=False)

            slots_logger.info(
                'User `{id_user}`: Dont have additional send slots'.format(id_user=call.from_user.id)
            )

        else:
            await call.message.edit_text(
                'У вас нет дополнительных слотов, вы не можете удалять базовые слоты'
            )
            await state.reset_state(with_data=False)

            slots_logger.info(
                'User `{id_user}`: Dont have additional slots'.format(id_user=call.from_user.id)
            )


# Удаление занятого слота и группы, занявшей этот слот, из всех связей
@dp.message_handler(state=States.DelOccupiedSlotState)
async def accept_del_occupied_slot(message: Message, state: FSMContext):
    id_user = message.from_user.id

    try:
        com = int(message.text[1:])

        async with state.proxy() as data:
            slot_type = data.get('current_slot_type')
            slots_dict = data.get('slot_indexes')

            group = slots_dict.get(com)

            stmt = select(
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
            )

            if slot_type == 'collect':
                data[id_user]['additionally_search_group'] = data.get(id_user).get('additionally_search_group') - 1
                get_current_group_stmt = stmt. \
                    filter(GroupsTable.main_group_name == group[0]).\
                    filter(id_user == GroupsTable.user_ids.any_())

            else:
                data[id_user]['additionally_send_group'] = data.get(id_user).get('additionally_send_group') - 1
                get_current_group_stmt = stmt. \
                    filter(GroupsTable.send_to_group_name == group[0]).\
                    filter(id_user == GroupsTable.user_ids.any_())

            if group:
                user = data.get(id_user)
                user_stmt = update_user_stmt(user)

                if com in slots_dict.keys():
                    res = await async_session.execute(get_current_group_stmt)

                    for rls in res.all():
                        to_update = {}

                        for key in rls.keys():
                            to_update[key] = rls[key]

                        user_ids = to_update.get('user_ids')
                        user_ids.remove(id_user)

                        to_update['user_ids'] = user_ids

                        insert_stmt = insert(GroupsTable).values(**to_update)

                        do_update_stmt = insert_stmt.on_conflict_do_update(
                            index_elements=['id'],
                            set_=to_update
                        )

                        await async_session.execute(do_update_stmt)

                    msg = 'Удалено из всех связей!\n\n<b><a href="{url}">{name}</a></b>'.format(
                        name=group[0],
                        url=group[1]
                    )
                    await message.answer(msg, parse_mode='HTML', reply_markup=ReplyKeyboardRemove())

                    await state.reset_state(with_data=True)

                    await async_session.execute(user_stmt)
                    await async_session.commit()

                    slots_logger.info(
                        'User `{id_user}`: Remove user from group in DB:: {group}'.format(id_user=id_user, group=group)
                    )

                else:
                    await message.answer('Не понимаю :/')
            else:
                await message.answer('Не понимаю :/')

    except ValueError as ex:

        slots_logger.exception(
            'User `{id_user}`: Wrong command \'{cmd}\'\n {ex}'.format(id_user=id_user, cmd=message.text, ex=ex)
        )

        await message.answer('Не понимаю :/')


# Подтверждение удаления свободного слота
@dp.callback_query_handler(callback_choice.filter(choice='yes'), state=States.DelEmptySlotState)
async def accept_del_empty_slot(call: CallbackQuery, state: FSMContext):
    id_user = call.from_user.id

    async with state.proxy() as data:
        slot_type = data.get(id_user).get('current_slot_type')

        if slot_type == 'collect':
            data[id_user]['additionally_search_group'] = data.get(id_user).get('additionally_search_group') - 1
        else:
            data[id_user]['additionally_send_group'] = data.get(id_user).get('additionally_send_group') - 1

        del data['current_slot_type']

        user = data.get(call.from_user.id)

        stmt = update_user_stmt(user)

        await async_session.execute(stmt)
        await async_session.commit()

    await call.message.edit_text('Удалено')
    await state.reset_state(with_data=False)

    slots_logger.info('User `{id_user}`: Deleted {type} slot'.format(id_user=call.from_user.id, type=slot_type))
