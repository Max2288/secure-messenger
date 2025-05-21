from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.app.settings import Settings


def get_config():
    return Settings()


def get_engine(config: Annotated[Settings, Depends(get_config)]):
    return create_async_engine(
        config.postgres.POSTGRES_URL,
        echo=False,
        pool_size=10,
        pool_pre_ping=True,
        max_overflow=0,
        future=True,
    )


async def get_pg_session(engine: Annotated[AsyncEngine, Depends(get_engine)]):
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as async_session:
        try:
            yield async_session
        finally:
            await async_session.close()