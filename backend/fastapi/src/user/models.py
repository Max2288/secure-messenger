from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.app.postgres.base import DEFAULT_SCHEMA, BaseModel
from src.app.postgres.timestamp_base import TimestampMixin


class User(BaseModel, TimestampMixin):
    __tablename__ = "user"
    __table_args__ = {
        "schema": DEFAULT_SCHEMA,
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    public_key: Mapped[str] = mapped_column(Text)

