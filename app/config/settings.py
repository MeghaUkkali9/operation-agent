from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Terminal Operations Assistant"
    app_version: str = "0.1.0"
    environment: Literal["local", "staging", "production"] = "local"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://terminal:terminal@localhost:5433/terminal_assistant"
    test_database_url: str = "postgresql+psycopg://terminal:terminal@localhost:5433/terminal_assistant_test"

    chunk_size: int = 500
    chunk_overlap: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()
