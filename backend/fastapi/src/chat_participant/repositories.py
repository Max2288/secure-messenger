import dataclasses
from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat_participant.models import ChatParticipant
from src.chat_participant.schemas.api.v1 import ChatParticipantCreate, ChatParticipantUpdate


@dataclasses.dataclass
class ChatParticipantRepository:
    session: AsyncSession

    async def create(self, payload: ChatParticipantCreate) -> ChatParticipant:
        participant = ChatParticipant(**payload.model_dump())
        self.session.add(participant)
        await self.session.commit()
        await self.session.refresh(participant)
        return participant

    async def get_by_id(self, participant_id: int) -> ChatParticipant | None:
        result = await self.session.execute(select(ChatParticipant).where(ChatParticipant.id == participant_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[ChatParticipant]:
        result = await self.session.execute(select(ChatParticipant))
        return result.scalars().all()

    async def update(self, participant_id: int, payload: ChatParticipantUpdate) -> ChatParticipant | None:
        participant = await self.get_by_id(participant_id)
        if participant is None:
            return None

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(participant, key, value)

        self.session.add(participant)
        await self.session.commit()
        await self.session.refresh(participant)
        return participant

    async def delete(self, participant_id: int) -> None:
        await self.session.execute(delete(ChatParticipant).where(ChatParticipant.id == participant_id))
        await self.session.commit()

    async def get_users_by_chat(self, chat_id: int) -> list[ChatParticipant]:
        stmt = select(ChatParticipant).where(ChatParticipant.chat_id == chat_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
