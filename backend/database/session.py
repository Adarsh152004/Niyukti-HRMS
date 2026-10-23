"""
Database Session — async_sessionmaker and FastAPI session dependency.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.database.engine import get_async_engine

# Session factory for creating AsyncSession instances
AsyncSessionLocal = async_sessionmaker(
    bind=get_async_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding a thread/async-safe AsyncSession.
    Rolls back automatically on exception and closes cleanly.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
