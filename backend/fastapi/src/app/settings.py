from pathlib import Path

from pydantic_settings import SettingsConfigDict

from src.app.base_settings import BaseSettings, Env, Postgres
from src.app.root import root_dir

env_file = Path(root_dir, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore",
        env_file=env_file,
    )
    port: int = 1026

    postgres: Postgres

    BASE_URL: str
    CENTRIFUGO_API_KEY: str
    CENTRIFUGO_API_URL: str
    CENTRIFUGO_CLIENT_SECRET_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SECRET_KEY: str
    SOCKET_URL: str

    env: Env = "local"

    PATH_PREFIX: str = "/api/v1"
