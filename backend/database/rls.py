"""
PostgreSQL Row-Level Security (RLS) — Session scoping & DDL policy helpers.

Enforces DB-level tenant boundaries as defense-in-depth behind application checks.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_tenant_session_context(session: AsyncSession, organization_id: str) -> None:
    """
    Set PostgreSQL session variable `app.current_organization_id` for RLS.

    Uses `SET LOCAL` so the variable setting is scoped strictly to the current transaction.
    """
    await session.execute(
        text("SET LOCAL app.current_organization_id = :org_id"),
        {"org_id": organization_id},
    )


def generate_rls_policy_ddl(table_name: str) -> list[str]:
    """
    Generate SQL DDL commands to enable RLS and create tenant isolation policy on a table.
    """
    policy_name = f"tenant_isolation_policy_{table_name}"
    return [
        f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;",
        f"DROP POLICY IF EXISTS {policy_name} ON {table_name};",
        f"CREATE POLICY {policy_name} ON {table_name} "
        f"FOR ALL USING (organization_id = current_setting('app.current_organization_id', true));",
    ]
