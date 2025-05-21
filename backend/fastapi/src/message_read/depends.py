from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from src.app.depends import get_pg_session
from src.message_read.repositories import MessageReadRepository


def get_message_read_repository(
    session: Annotated[AsyncSession, Depends(get_pg_session)],
) -> MessageReadRepository:
    return MessageReadRepository(session=session)
