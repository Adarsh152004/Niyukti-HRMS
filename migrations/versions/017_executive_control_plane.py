"""
Alembic Migration 017 — Executive Control Plane, Autonomy Matrix, Kill Switch, and Quarantine.

Revision ID: 017_executive_control_plane
Revises: 016_multi_agent_operations
Create Date: 2026-08-30 13:18:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "017_executive_control_plane"
down_revision = "016_multi_agent_operations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Kill Switch Audit Log
    op.create_table(
        "hrms_executive_kill_switch_logs",
        sa.Column("log_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("action", sa.String(32), nullable=False),  # ACTIVATED / DEACTIVATED
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("triggered_by", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 2. Agent Autonomy Matrix Overrides
    op.create_table(
        "hrms_agent_autonomy_matrix",
        sa.Column("setting_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("agent_role", sa.String(64), nullable=False),
        sa.Column("autonomy_mode", sa.String(64), nullable=False),
        sa.Column("updated_by", sa.String(64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 3. Agent Quarantine Records
    op.create_table(
        "hrms_agent_quarantine_records",
        sa.Column("record_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("agent_role", sa.String(64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("quarantined_by", sa.String(64), nullable=False),
        sa.Column("quarantined_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("hrms_agent_quarantine_records")
    op.drop_table("hrms_agent_autonomy_matrix")
    op.drop_table("hrms_executive_kill_switch_logs")
