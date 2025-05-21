from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.postgres.timestamp_base import TimestampMixin
from src.app.postgres.base import DEFAULT_SCHEMA, BaseModel


class ChatParticipant(BaseModel, TimestampMixin):
    __tablename__ = "chat_participant"
    __table_args__ = {
        "schema": DEFAULT_SCHEMA,
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.chat.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.user.id"))
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()
