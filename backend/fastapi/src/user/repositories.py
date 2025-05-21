import dataclasses
from typing import Optional, Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.models import User


@dataclasses.dataclass
class UserRepository:
    """Репозиторий для взаимодействия с пользователями."""

    session: AsyncSession

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(self, limit: int = 100, offset: int = 0) -> Sequence[User]:
        stmt = select(User).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_user(self, username: str, password_hash: str, public_key: str) -> User:
        user = User(username=username, password_hash=password_hash, public_key=public_key)
        self.session.add(user)
        await self.session.commit()
        return user

    async def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        password_hash: Optional[str] = None,
        public_key: Optional[str] = None,
    ) -> Optional[User]:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                **{
                    k: v
                    for k, v in {
                        "username": username,
                        "password_hash": password_hash,
                        "public_key": public_key,
                    }.items()
                    if v is not None
                }
            )
            .returning(User)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete_user(self, user_id: int) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def login_user(self, username: str, password_hash: str) -> User | None:
        user = await self.session.scalar(select(User).where(User.username == username))
        if not user or user.password_hash != password_hash:
            return None

        return user
