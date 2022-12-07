import logging.config

from sqlalchemy import inspect

from db import Base, engine, UsersTable, GroupsTable
from utils.logging import dict_config, async_dec_logger

logging.config.dictConfig(dict_config)
init_db_logger = logging.getLogger('init_db')


@async_dec_logger(init_db_logger)
async def init_db() -> None:
    async with engine.begin() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )

        if UsersTable.__tablename__ and GroupsTable.__tablename__ not in tables:
            await conn.run_sync(Base.metadata.create_all)
            init_db_logger.info('Initialization database')

        await engine.dispose()
