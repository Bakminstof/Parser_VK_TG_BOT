from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from data import DB_URI

engine = create_async_engine(DB_URI)
Base = declarative_base(bind=engine)

session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async_session = session()
