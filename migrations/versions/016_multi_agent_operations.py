"""
Alembic Migration 016 — Multi-Agent Business Operations, Teams, and Collusion Auditing.

Revision ID: 016_multi_agent_operations
Revises: 015_autonomous_workflows
Create Date: 2026-08-30 13:14:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "016_multi_agent_operations"
down_revision = "015_autonomous_workflows"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Multi-Agent Inter-Agent Messages Journal
    op.create_table(
        "hrms_agent_messages",
        sa.Column("message_id", sa.String(64), primary_key=True),
        sa.Column("conversation_id", sa.String(64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("sender_role", sa.String(64), nullable=False),
        sa.Column("recipient_role", sa.String(64), nullable=False),
        sa.Column("message_type", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("priority", sa.String(32), nullable=False, server_default="NORMAL"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )

    # 2. Collusion & Privilege Escalation Audit Alerts
    op.create_table(
        "hrms_collusion_alerts",
        sa.Column("alert_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("violation_type", sa.String(64), nullable=False),
        sa.Column("sender_role", sa.String(64), nullable=False),
        sa.Column("recipient_role", sa.String(64), nullable=False),
        sa.Column("message_id", sa.String(64), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("hrms_collusion_alerts")
    op.drop_table("hrms_agent_messages")
