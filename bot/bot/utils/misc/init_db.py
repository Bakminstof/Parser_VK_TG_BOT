import logging.config

from os.path import isfile
from sqlalchemy import inspect

from db import Base_main, main_engine, UsersTable, GroupsTable, Base_logs, logs_engine
from data import LOGS_DB_NAME
from utils.logging import dict_config, async_dec_logger

logging.config.dictConfig(dict_config)
init_db_logger = logging.getLogger('init_db')


@async_dec_logger(init_db_logger)
async def init_db() -> None:
    async with main_engine.begin() as main_conn:
        tables = await main_conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )

        if UsersTable.__tablename__ and GroupsTable.__tablename__ not in tables:
            await main_conn.run_sync(Base_main.metadata.create_all)
            init_db_logger.info('Initialization main database')

        await main_engine.dispose()

    if not isfile(LOGS_DB_NAME):
        async with logs_engine.begin() as logs_conn:
            await logs_conn.run_sync(Base_logs.metadata.create_all)
            init_db_logger.info('Initialization logs database')

        await logs_engine.dispose()
