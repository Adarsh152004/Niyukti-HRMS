"""
Database Configuration - Environment-driven database settings.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """
    Database connection settings loaded from environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite+aiosqlite:///./hrms.db"
    test_database_url: str = "sqlite+aiosqlite:///./hrms_test.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False
    database_pool_pre_ping: bool = True
    database_enabled: bool = True


@lru_cache
def get_db_settings() -> DatabaseSettings:
    """Return cached DatabaseSettings instance."""
    return DatabaseSettings()
