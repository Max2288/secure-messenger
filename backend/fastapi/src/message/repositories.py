import dataclasses
from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.message.models import Message
from src.message.schemas.api.v1 import MessageCreate, MessageUpdate


@dataclasses.dataclass
class MessageRepository:
    session: AsyncSession

    async def create(self, payload: MessageCreate) -> Message:
        message = Message(**payload.model_dump())
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_by_id(self, message_id: int) -> Message | None:
        result = await self.session.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[Message]:
        result = await self.session.execute(select(Message))
        return result.scalars().all()

    async def update(self, message_id: int, payload: MessageUpdate) -> Message | None:
        message = await self.get_by_id(message_id)
        if message is None:
            return None

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(message, key, value)

        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def delete(self, message_id: int) -> None:
        await self.session.execute(delete(Message).where(Message.id == message_id))
        await self.session.commit()

    async def get_by_chat_id(self, chat_id: int) -> list[Message]:
        stmt = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()
