import asyncio
import datetime

from sqlalchemy import delete

from db.schemas import BaseLoggerTable
from db.database import async_session

LOG_CACHE = []


# autocommit logs
async def autocommit_logs():
    lock = asyncio.Lock()

    while True:
        await asyncio.sleep(10)

        async with lock:
            async_session.add_all(LOG_CACHE)

            LOG_CACHE.clear()

        await async_session.commit()


# remove old logs
async def autoremove_logs():
    last_day: datetime.datetime | None = None

    while True:
        current_day = datetime.datetime.now()

        if last_day and (last_day.date() != current_day.date()):
            delta = current_day - datetime.timedelta(days=1)

            del_stmt = delete(BaseLoggerTable).filter(BaseLoggerTable.dtime <= delta)

            await async_session.execute(del_stmt)

        last_day = current_day

        await asyncio.sleep(3600 * 4)
