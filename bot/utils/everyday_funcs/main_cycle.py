import asyncio
import datetime
import logging.config

from data import REFRESH_TIME
from loader import bot
from hendlers import dp
from utils.logging import dict_config, async_dec_logger
from utils.everyday_funcs.collect import collect_all
from utils.everyday_funcs.backup_db import backup
from utils.everyday_funcs.clear_cache import clear_cache_and_content_directories
from utils.everyday_funcs.send_all_posts import send_all
from utils.everyday_funcs.user_management import user_mgmt

logging.config.dictConfig(dict_config)
main_cycle_logger = logging.getLogger('main_cycle')


@async_dec_logger(main_cycle_logger)
async def mian_cycle():
    last_day = datetime.date.today()

    while True:
        today = datetime.date.today()

        await collect_all()

        await send_all(bot)

        clear_cache_and_content_directories()

        if last_day != today:
            last_day = today

            await user_mgmt(dp=dp, day=today)

            await backup()

        await asyncio.sleep(REFRESH_TIME)
