from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from config import LOGS_DB_URI


engine_log = create_async_engine(LOGS_DB_URI)

async_session = sessionmaker(
    bind=engine_log,
    expire_on_commit=False,
    class_=AsyncSession
)

a_session_log = async_session()
