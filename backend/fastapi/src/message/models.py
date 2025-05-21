from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.postgres.timestamp_base import TimestampMixin
from src.app.postgres.base import DEFAULT_SCHEMA, BaseModel


class Message(BaseModel, TimestampMixin):
    __tablename__ = "message"
    __table_args__ = {
        "schema": DEFAULT_SCHEMA,
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.chat.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.user.id"))
    encrypted_payload: Mapped[bytes] = mapped_column(LargeBinary)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()
    reads: Mapped[list["MessageRead"]] = relationship(back_populates="message")
