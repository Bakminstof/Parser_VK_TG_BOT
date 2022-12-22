import datetime
import logging.config

from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from db import async_mian_session, UsersTable, get_user_by_telegram_id_stmt
from data import START_MESSAGE
from loader import dp
from utils.logging import dict_config
from keyboards.default.d_start import start_wo_subs_keyboard, start_with_subs_keyboard, start_subs_keyboard

logging.config.dictConfig(dict_config)
start_logger = logging.getLogger('start')


@dp.message_handler(commands=['start'], state=None)
async def start(message: Message, state: FSMContext):
    async with state.proxy() as data:
        user_cache = data.get(message.from_user.id)

    if not user_cache:
        stmt = get_user_by_telegram_id_stmt(message.from_user.id)

        res = await async_mian_session.execute(stmt)
        check = res.one_or_none()

        if not check:
            t_id = message.from_user.id
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            date_auth = datetime.datetime.now()

            new_user = UsersTable(
                telegram_id=t_id,
                first_name=first_name,
                last_name=last_name,
                date_auth=date_auth
            )

            async_mian_session.add(new_user)

            await async_mian_session.commit()

            stmt = get_user_by_telegram_id_stmt(message.from_user.id)
            res = await async_mian_session.execute(stmt)
            check = res.one_or_none()

            start_logger.info('Добавлен новый пользователь: {}'.format(message.from_user.first_name))

        user = {}

        for key in check.keys():
            user[key] = check[key]

        async with state.proxy() as data:
            data[message.from_user.id] = user
            user_cache = user

    subs = user_cache.get('subscription')
    test = user_cache.get('subscription_test_period')

    if not test and not subs:
        keyboard = start_wo_subs_keyboard
    elif test and not subs:
        keyboard = start_subs_keyboard
    else:
        keyboard = start_with_subs_keyboard

    await message.answer(
        START_MESSAGE,
        reply_markup=keyboard
    )
