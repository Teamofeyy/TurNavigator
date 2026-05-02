from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from app.core.env import load_env_files


def _read_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    postgres_db: str = "travelcontext"
    postgres_user: str = "travelcontext"
    postgres_password: str = "travelcontext"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 54329
    database_url: str | None = None
    sqlalchemy_echo: bool = False

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    load_env_files()
    postgres_port_raw = os.getenv("POSTGRES_PORT", "54329")
    try:
        postgres_port = int(postgres_port_raw)
    except ValueError:
        postgres_port = 54329

    return Settings(
        postgres_db=os.getenv("POSTGRES_DB", "travelcontext"),
        postgres_user=os.getenv("POSTGRES_USER", "travelcontext"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "travelcontext"),
        postgres_host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        postgres_port=postgres_port,
        database_url=os.getenv("DATABASE_URL"),
        sqlalchemy_echo=_read_bool(os.getenv("SQLALCHEMY_ECHO"), default=False),
    )
