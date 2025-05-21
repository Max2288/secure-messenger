from datetime import datetime

from sqlalchemy import TIMESTAMP, MetaData, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declarative_mixin, declared_attr, mapped_column, registry


DEFAULT_SCHEMA = "messenger_encrypted"

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

mapper_registry = registry(
    metadata=MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION),
)


class BaseModel(DeclarativeBase, AsyncAttrs):
    """Базовая абстрактная модель для всех моделей SQL Alchemy."""

    registry = mapper_registry
    metadata = mapper_registry.metadata
