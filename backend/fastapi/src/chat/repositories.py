import dataclasses
from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.models import Chat
from src.chat.schemas.api.v1 import ChatCreate, ChatUpdate
from src.chat_participant.models import ChatParticipant


@dataclasses.dataclass
class ChatRepository:
    """Репозиторий для взаимодействия с чатами."""

    session: AsyncSession

    async def create(self, payload: ChatCreate) -> Chat:
        chat = Chat(**payload.model_dump())
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def get_by_id(self, chat_id: int) -> Chat | None:
        result = await self.session.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[Chat]:
        result = await self.session.execute(select(Chat))
        return result.scalars().all()

    async def update(self, chat_id: int, payload: ChatUpdate) -> Chat | None:
        chat = await self.get_by_id(chat_id)
        if chat is None:
            return None

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(chat, key, value)

        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def delete(self, chat_id: int) -> None:
        await self.session.execute(delete(Chat).where(Chat.id == chat_id))
        await self.session.commit()

    async def get_chats_by_user(self, user_id: int) -> list[Chat]:
        stmt = (
            select(Chat)
            .join(ChatParticipant)
            .where(ChatParticipant.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
