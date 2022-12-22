import asyncio
import datetime
import logging.config

from typing import Dict, List
from aiogram import Dispatcher

from db import async_mian_session, get_all_users_stmt, update_user_stmt
from utils.logging import dict_config

logging.config.dictConfig(dict_config)
user_mgmt_logger = logging.getLogger('user_mgmt')


async def user_mgmt(dp: Dispatcher, day: datetime.date):
    res = await async_mian_session.execute(get_all_users_stmt())
    users_rows = res.all()

    users: List[Dict] = []
    reset_states_tasks = []

    for user_row in users_rows:
        user_id = user_row.telegram_id

        reset_states_tasks.append(dp.storage.reset_state(user=user_id))

        user = {}

        for key in user_row.keys():
            user[key] = user_row[key]

        users.append(user)

    await asyncio.gather(*reset_states_tasks)

    user_mgmt_logger.info('Reset users states')

    update_tasks = []
    subs_notif_tasks = []

    for user in users:
        user_id = user.get('id')
        username = user.get('first_name')

        user['total_subscription_days'] = user.get('total_subscription_days', 0) + 1

        date_end_subscription: datetime.date = user.get('date_end_subscription')
        check = date_end_subscription - day
        left_days = check.days

        if left_days == 0:
            user['subscription'] = False
            user['date_end_subscription'] = None
            user['additionally_search_group'] = None
            user['additionally_send_group'] = None

            msg = 'Подписка закончилась!'
            subs_notif_tasks.append(dp.bot.send_message(chat_id=user_id, text=msg))

            log_ = 'End of user\'s subscription: ({}, {})'.format(username, user_id)
            user_mgmt_logger.warning(log_)

        elif left_days in (1, 2, 3):
            msg = 'У вас осталось дней до окончании подписки: {}'.format(left_days)
            subs_notif_tasks.append(dp.bot.send_message(chat_id=user_id, text=msg))

            log_ = 'Few days ({}) of user\'s subscription: ({}, {})'.format(left_days, username, user_id)
            user_mgmt_logger.info(log_)

        update_tasks.append(async_mian_session.execute(update_user_stmt(user)))

    await asyncio.gather(*update_tasks)
    await asyncio.gather(*subs_notif_tasks)

    log_ = 'Complete users management'
    user_mgmt_logger.info(log_)
