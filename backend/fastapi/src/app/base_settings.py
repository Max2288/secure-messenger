from enum import Enum

from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Env(str, Enum):
    test = "test"
    local = "local"
    dev = "dev"
    qa = "qa"
    prod = "prod"


class LogLevel(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"
    debug = "debug"


class LogFormat(str, Enum):
    json = "json"
    text = "text"


class Postgres(BaseSettings):
    POSTGRES_URL: str


class BaseSettings(PydanticBaseSettings):
    log_level: LogLevel = LogLevel.debug
    log_format: LogFormat = LogFormat.text
