from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.postgres.timestamp_base import TimestampMixin
from src.app.postgres.base import DEFAULT_SCHEMA, BaseModel


class ChatType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


class Chat(BaseModel, TimestampMixin):
    __tablename__ = "chat"
    __table_args__ = {
        "schema": DEFAULT_SCHEMA,
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    chat_type: Mapped[ChatType] = mapped_column(String)

    participants: Mapped[list["ChatParticipant"]] = relationship(back_populates="chat")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat")

