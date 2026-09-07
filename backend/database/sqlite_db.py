"""
SQLite Database Connection, Transaction & Audit Logging Management.
Enforces WAL mode, foreign keys, row factories, and tenant isolation.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aiosqlite

logger = logging.getLogger(__name__)


def get_sqlite_db_path() -> str:
    """Resolve active database path from environment or local defaults."""
    env_path = os.getenv("DATABASE_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    if os.path.exists("hrms.db"):
        return "hrms.db"
    if os.path.exists("backend/hrms.db"):
        return "backend/hrms.db"
    return "hrms.db"


@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    Yields an aiosqlite Connection configured with:
    - WAL Journal Mode (concurrency safety)
    - Foreign Keys enabled
    - Row factory enabled (dict-like row access)
    - 5000ms busy timeout
    """
    db_path = get_sqlite_db_path()
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row

    try:
        await conn.execute("PRAGMA journal_mode = WAL;")
        await conn.execute("PRAGMA foreign_keys = ON;")
        await conn.execute("PRAGMA busy_timeout = 5000;")
        yield conn
    finally:
        await conn.close()


async def init_sqlite_db() -> None:
    """Idempotently initialize required tables (e.g. work_logs) and indexes."""
    async with get_db_connection() as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS work_logs (
                id VARCHAR(64) PRIMARY KEY,
                organization_id VARCHAR(64) NOT NULL,
                employee_id VARCHAR(64) NOT NULL,
                task_id VARCHAR(64),
                work_date DATE NOT NULL,
                description TEXT NOT NULL,
                hours_spent FLOAT NOT NULL DEFAULT 1.0,
                blockers TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );
            """
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_work_logs_org_emp ON work_logs(organization_id, employee_id, work_date);"
        )
        await db.commit()
        logger.info("SQLite database verified and work_logs table initialized.")


async def record_audit_log(
    conn: aiosqlite.Connection,
    organization_id: str,
    actor_id: str,
    actor_type: str,
    action: str,
    entity_type: str,
    entity_id: str,
    changes: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> str:
    """Records an immutable audit event in audit_logs."""
    audit_id = f"aud-{uuid.uuid4().hex[:12]}"
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    changes_json = json.dumps(changes or {})

    await conn.execute(
        """
        INSERT INTO audit_logs (
            id, organization_id, user_id, actor_type, action, 
            entity_type, entity_id, changes_json, ip_address, user_agent, occurred_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            audit_id,
            organization_id,
            actor_id,
            actor_type,
            action,
            entity_type,
            entity_id,
            changes_json,
            ip_address or "127.0.0.1",
            user_agent or "HRMS-Core",
            now_str,
        ),
    )
    return audit_id
