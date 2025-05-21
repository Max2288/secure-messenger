from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.depends import get_pg_session
from src.message.repositories import MessageRepository


def get_message_repository(
    session: Annotated[AsyncSession, Depends(get_pg_session)],
) -> MessageRepository:
    return MessageRepository(session=session)
