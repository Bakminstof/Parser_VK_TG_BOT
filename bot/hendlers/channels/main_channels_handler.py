import logging.config


from typing import Tuple, List, Dict
from sqlalchemy import select
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext

from db import async_session, GroupsTable
from states import States
from loader import dp
from data.prices import BASE_SLOTS_COUNT
from utils.logging import dict_config
from keyboards.inline import channels_edit_keyboard
from hendlers.handlers_funcs import check_subscription_and_add_to_cache
from keyboards.default.d_start import start_wo_subs_keyboard, start_subs_keyboard
from keyboards.inline.callbacks import callback_channels

logging.config.dictConfig(dict_config)
channels_logger = logging.getLogger('channels')

CMD = 'channels'


@dp.callback_query_handler(callback_channels.filter(type='main_back'), state=States.EditRlsState)
@dp.message_handler(commands=[CMD], state=None)
async def channels(message_call: Message | CallbackQuery, state: FSMContext):
    if isinstance(message_call, Message):
        id_user = message_call.from_user.id
        message = message_call
        back = False
    else:
        id_user = message_call.from_user.id
        message = message_call.message
        back = True

    subs, test = await check_subscription_and_add_to_cache(id_user, state)

    rls_stmt = select(
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
    ).filter(id_user == GroupsTable.user_ids.any_())

    if subs:
        async with state.proxy() as data:
            rls: Dict[int, Dict[str, str | int]] = data.get('rls')

            if not rls:
                result = await async_session.execute(rls_stmt)
                rls_db = result.all()
                rls = {}

                for r in rls_db:
                    row = {}

                    for key in r.keys():
                        row[key] = r[key]

                    rls[r.id] = row

                data['rls'] = rls

            additionally_search_group = data.get(id_user).get('additionally_search_group', 0)
            additionally_send_group = data.get(id_user).get('additionally_send_group', 0)

            main_groups: set[Tuple[str, str]] = set()
            send_to_groups: set[Tuple[str, str]] = set()

            relationships: List[str] = []

            for row in rls.values():
                main_group = (row.get('main_group_name'), row.get('main_group_url'))
                send_to_group = (row.get('send_to_group_name'), row.get('send_to_group_url'))

                main_groups.add(main_group)
                send_to_groups.add(send_to_group)

                relationships.append(
                    '----\n<b><a href="{main_url}">{main_name}</a></b>'
                    ' \u27a1\ufe0f '
                    '<b><a href="{send_to_url}">{send_to_name}</a></b>'.format(
                        main_url=row.get('main_group_url'),
                        main_name=row.get('main_group_name'),
                        send_to_url=row.get('send_to_group_url'),
                        send_to_name=row.get('send_to_group_name')
                    )
                )

            max_main_count = BASE_SLOTS_COUNT + additionally_search_group
            max_send_to_count = BASE_SLOTS_COUNT + additionally_send_group

            current_main_count = len(main_groups)
            current_send_to_count = len(send_to_groups)

            data['current_main_count'] = current_main_count
            data['current_send_to_count'] = current_send_to_count
            data['main_groups'] = main_groups
            data['send_to_groups'] = send_to_groups

        from_ = [
            '----\n<b><a href="{url}">{name}</a></b>'.format(name=name, url=url) for name, url in main_groups
        ]
        to_ = [
            '----\n<b><a href="{url}">{name}</a></b>'.format(name=name, url=url) for name, url in send_to_groups
        ]

        msg = '<b><i>Откуда брать информацию ' \
              '(текущие: {current_main}, макс.: {max_main}):</i></b>\n{from_}\n----\n\n' \
              '<b><i>Куда оправлять информацию ' \
              '(текущие: {current_send_to}, макс.: {max_send_to}):</i></b>\n{to_}\n----\n\n' \
              '<b><i>Связи:</i></b>\n{rls_}\n----\n'.format(
                from_='\n'.join(from_),
                to_='\n'.join(to_),
                rls_='\n'.join(relationships),
                max_main=max_main_count,
                max_send_to=max_send_to_count,
                current_main=current_main_count,
                current_send_to=current_send_to_count
              )

        if back:
            await message.edit_text(
                msg,
                parse_mode='HTML',
                reply_markup=channels_edit_keyboard,
                disable_web_page_preview=True
            )
        else:
            await message.answer(
                msg,
                parse_mode='HTML',
                reply_markup=channels_edit_keyboard,
                disable_web_page_preview=True
            )

        channels_logger.info('User `{id_user}` -> {cmd}'.format(id_user=id_user, cmd=CMD))

    else:
        if not test and not subs:
            keyboard = start_wo_subs_keyboard
        else:
            keyboard = start_subs_keyboard

        await message.answer('У вас нет подписки :/', reply_markup=keyboard)

        channels_logger.info('User `{id_user}` dont have subscription'.format(id_user=id_user))

    await state.reset_state(with_data=False)
