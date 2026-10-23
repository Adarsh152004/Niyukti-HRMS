"""
Database Health Check — Connection, query execution, and session availability inspection.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import text

from backend.database.engine import get_async_engine


async def check_database_health() -> dict[str, Any]:
    """
    Inspect database health without exposing sensitive credentials.

    Returns:
        Dict with status, engine status, and latency.
    """
    engine = get_async_engine()
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                pool_size = getattr(engine.pool, "size", lambda: 0)()
                return {
                    "status": "healthy",
                    "database": "connected",
                    "driver": "asyncpg",
                    "pool_size": pool_size,
                }
            return {"status": "unhealthy", "error": "Query returned unexpected scalar"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }
