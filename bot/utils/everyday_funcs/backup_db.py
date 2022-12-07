import datetime
import logging.config
import os
import shutil

from typing import List
from pathlib import Path

from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.serializer import loads, dumps

from db import async_session, get_all_rls_stmt, get_all_users_stmt
from utils.logging import dict_config

logging.config.dictConfig(dict_config)
backup_logger = logging.getLogger('backup')


async def _do_backup(data: bytes, path: Path, table_name: str):
    last_backup_date: datetime.date | None = None

    current_date = datetime.date.today()

    if last_backup_date is None:
        last_backup_date = current_date

    old = current_date - last_backup_date

    days = old.days

    current_week_dir = path / str(last_backup_date.isoweekday())

    if days >= 7:
        current_week_dir = path / str(current_date.isoweekday())

        items: List[str] = os.listdir(path)

        for item in items:
            if item != current_week_dir.name:
                item = path / item
                shutil.rmtree(item)

    if not os.path.exists(current_week_dir):
        os.mkdir(current_week_dir)

    current_day_dir = current_week_dir / str(current_date.today())

    if not os.path.exists(current_day_dir):
        os.mkdir(current_day_dir)

    backup_filename = current_day_dir / table_name

    with open(backup_filename, 'wb') as file:
        file.write(data)

    backup_logger.info('Done backup: {}'.format(backup_filename))


async def backup() -> None:
    backup_path = Path(__file__).parent.parent.parent / 'db' / 'backup_data'

    groups_stmt = get_all_rls_stmt()
    users_stmt = get_all_users_stmt()

    groups_result = await async_session.execute(groups_stmt)
    users_result = await async_session.execute(users_stmt)

    serialized_data_groups: bytes = dumps(groups_result.all())
    serialized_data_users: bytes = dumps(users_result.all())

    await _do_backup(serialized_data_users, backup_path, 'users')
    await _do_backup(serialized_data_groups, backup_path, 'groups')


async def restore(data: bytes, metadata: MetaData, session: AsyncSession):
    restore_data = loads(data, metadata, session)

    await session.merge(restore_data)
    await session.commit()
