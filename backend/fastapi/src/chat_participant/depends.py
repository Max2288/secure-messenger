from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from src.app.depends import get_pg_session
from src.chat_participant.repositories import ChatParticipantRepository


def get_chat_participant_repository(
    session: Annotated[AsyncSession, Depends(get_pg_session)],
) -> ChatParticipantRepository:
    return ChatParticipantRepository(session=session)
