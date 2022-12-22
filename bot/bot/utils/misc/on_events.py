import asyncio
import logging.config

from asyncio import gather

# from loader import SSL_CERTIFICATE
from db import async_mian_session, main_engine, async_logs_session, logs_engine
from data import ADMINS#, WEBHOOK_URL
from loader import dp, qiwi_api
from utils.logging import dict_config
from db.management_logs import autocommit_logs, autoremove_logs
from utils.misc.init_db import init_db
from utils.misc.set_bot_commands import set_default_commands
from utils.everyday_funcs.main_cycle import mian_cycle


logging.config.dictConfig(dict_config)
notify_logger = logging.getLogger('notify')


## startup event
async def on_startup(dispatcher):
    loop = asyncio.get_running_loop()
    # await dp.bot.set_webhook(
    #     url=WEBHOOK_URL,
    #     certificate=SSL_CERTIFICATE
    # )

    await set_default_commands(dispatcher)
    await on_startup_notify()

    loop.create_task(mian_cycle())
    loop.create_task(autocommit_logs())
    loop.create_task(autoremove_logs())


# startup notify
async def on_startup_notify():
    await init_db()

    message = 'Бот Запущен'
    tasks = [dp.bot.send_message(admin, "<b>{}</b>".format(message), parse_mode='HTML') for admin in ADMINS]

    notify_logger.info(message)
    await gather(*tasks)


## shutdown event
# shutdown notify
async def on_shutdown(dispatcher):
    message = 'Бот завершил работу'
    tasks = [dp.bot.send_message(admin, "<b>{}</b>".format(message), parse_mode='HTML') for admin in ADMINS]

    notify_logger.info(message)

    await gather(*tasks)
    await _graceful_stop()


async def _graceful_stop():
    notify_logger.info('Graceful stopping ...')

    await async_mian_session.commit()
    await async_logs_session.commit()

    await async_mian_session.close()
    await async_logs_session.close()

    await main_engine.dispose()
    await logs_engine.dispose()

    qiwi_api.stop()
