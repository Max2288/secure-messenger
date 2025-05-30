from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from src.app.depends import get_pg_session
from src.user.repositories import UserRepository


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_pg_session)],
) -> UserRepository:
    return UserRepository(session=session)
