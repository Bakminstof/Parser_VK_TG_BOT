from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from data import MAIN_DB_URI, LOGS_DB_URI

# Main DB setting
main_engine = create_async_engine(MAIN_DB_URI)
Base_main = declarative_base(bind=main_engine)

mian_session = sessionmaker(
    bind=main_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async_mian_session = mian_session()

# Logs DB setting
logs_engine = create_async_engine(LOGS_DB_URI)
Base_logs = declarative_base(bind=logs_engine)

logs_session = sessionmaker(
    bind=logs_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async_logs_session = logs_session()
