import os
from typing import Literal
from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    PROJECT_NAME: str = "Virtual Banking Core API"
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn
    JWT_SECRET_KEY: str
    ADMIN_EMAIL: str

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_async_pg(cls, v: PostgresDsn) -> PostgresDsn:
        url_str = str(v)
        if not url_str.startswith("postgresql+asyncpg://") and not url_str.startswith("sqlite+aiosqlite://"):
            raise ValueError("DATABASE_URL scheme must support async drivers (postgresql+asyncpg:// or sqlite+aiosqlite://)")
        return v

try:
    settings = AppSettings()
except Exception as e:
    # Fail-fast on startup configuration mismatch
    print("FATAL CONFIGURATION ERROR ENCOUNTERED:")
    raise e
