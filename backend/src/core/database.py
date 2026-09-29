from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base

from src.core.settings import Settings
from src.core.paths import DATABASE_ROOT, ENV_PATH
from src.core.logger import get_logger
from dotenv import load_dotenv

logger = get_logger(__name__)

load_dotenv(dotenv_path=ENV_PATH)


def get_database_url() -> str:
    if Settings.DATABASE.DATABASE_URL:
        return Settings.DATABASE.DATABASE_URL

    return f"sqlite+aiosqlite:///{DATABASE_ROOT}/test.db"


DATABASE_URL = get_database_url()

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {
        "check_same_thread": False,
        "timeout": 30,
    }

engine_kwargs = {
    "echo": Settings.DATABASE.SQL_ECHO,
}
if connect_args:
    engine_kwargs["connect_args"] = connect_args

if "postgresql" in DATABASE_URL:
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_size": Settings.DATABASE.DB_POOL_SIZE,
            "max_overflow": Settings.DATABASE.DB_MAX_OVERFLOW,
            "pool_timeout": Settings.DATABASE.DB_POOL_TIMEOUT,
            "pool_recycle": Settings.DATABASE.POOL_RECYCLE,
        }
    )

engine: AsyncEngine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            logger.error("Database error, rolling back")
            raise


@asynccontextmanager
async def get_db_context():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            logger.error("Database error, rolling back")
            raise


async def execute_with_retry(session: AsyncSession, stmt):
    return await session.execute(stmt)


async def close_db():
    await engine.dispose()
    logger.info("Database connections closed")
