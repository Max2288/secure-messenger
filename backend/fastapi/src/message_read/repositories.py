import dataclasses
from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.message_read.models import MessageRead
from src.message_read.schemas.api.v1 import MessageReadCreate


@dataclasses.dataclass
class MessageReadRepository:
    session: AsyncSession

    async def create(self, payload: MessageReadCreate) -> MessageRead:
        instance = MessageRead(**payload.model_dump())
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def has_user_read(self, message_id: int, user_id: int) -> bool:
        stmt = select(MessageRead).where(
            MessageRead.message_id == message_id,
            MessageRead.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_message(self, message_id: int) -> Sequence[MessageRead]:
        stmt = select(MessageRead).where(MessageRead.message_id == message_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_for_user(self, message_id: int, user_id: int) -> None:
        stmt = delete(MessageRead).where(
            MessageRead.message_id == message_id,
            MessageRead.user_id == user_id
        )
        await self.session.execute(stmt)
        await self.session.commit()


    async def mark_many_as_read(self, message_ids: list[int], user_id: int) -> None:
        existing_stmt = select(MessageRead.message_id).where(
            MessageRead.user_id == user_id,
            MessageRead.message_id.in_(message_ids)
        )
        existing_result = await self.session.execute(existing_stmt)
        existing_message_ids = {row[0] for row in existing_result.fetchall()}

        new_message_ids = set(message_ids) - existing_message_ids

        if new_message_ids:
            self.session.add_all([
                MessageRead(user_id=user_id, message_id=mid)
                for mid in new_message_ids
            ])
            await self.session.commit()

    async def get_read_message_ids(self, user_id: list[int], message_ids: list[int]) -> set[int]:
        if not message_ids:
            return set()

        stmt = select(MessageRead.message_id).where(
            MessageRead.user_id.in_(user_id),
            MessageRead.message_id.in_(message_ids)
        )
        result = await self.session.execute(stmt)
        return {row[0] for row in result.fetchall()}
