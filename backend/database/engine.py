"""
Database Engine - AsyncEngine setup supporting SQLite and PostgreSQL.
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from backend.database.config import get_db_settings


@lru_cache
def get_async_engine() -> AsyncEngine:
    """
    Create and return the singleton AsyncEngine instance.
    Handles SQLite and PostgreSQL pool options appropriately.
    """
    settings = get_db_settings()
    url = settings.database_url

    if url.startswith("sqlite"):
        return create_async_engine(
            url,
            echo=settings.database_echo,
            connect_args={"check_same_thread": False},
        )

    return create_async_engine(
        url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=settings.database_pool_pre_ping,
    )
