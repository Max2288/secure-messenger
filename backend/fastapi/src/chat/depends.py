from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.depends import get_pg_session
from src.chat.repositories import ChatRepository


def get_chat_repository(
    session: Annotated[AsyncSession, Depends(get_pg_session)],
) -> ChatRepository:
    return ChatRepository(session=session)
