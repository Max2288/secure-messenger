from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.postgres.base import DEFAULT_SCHEMA, BaseModel
from src.app.postgres.timestamp_base import TimestampMixin


class MessageRead(BaseModel, TimestampMixin):
    __tablename__ = "message_read"
    __table_args__ = {
        "schema": DEFAULT_SCHEMA,
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.message.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{DEFAULT_SCHEMA}.user.id"))

    message: Mapped["Message"] = relationship(back_populates="reads")
    user: Mapped["User"] = relationship()
