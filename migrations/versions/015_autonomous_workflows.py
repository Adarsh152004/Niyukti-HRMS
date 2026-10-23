"""
Alembic Migration 015 — Autonomous HR Workflows & Sagas.

Revision ID: 015_autonomous_workflows
Revises: 014_deterministic_hrms_platform
Create Date: 2026-08-30 12:55:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "015_autonomous_workflows"
down_revision = "014_deterministic_hrms_platform"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Saga Compensation Journal Table
    op.create_table(
        "hrms_saga_compensation_logs",
        sa.Column("log_id", sa.String(64), primary_key=True),
        sa.Column("execution_id", sa.String(64), nullable=False, index=True),
        sa.Column("step_id", sa.String(64), nullable=False),
        sa.Column("forward_command_type", sa.String(128), nullable=False),
        sa.Column("compensating_command_type", sa.String(128), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 2. HITL Workflow Suspension Tokens
    op.create_table(
        "hrms_hitl_workflow_tokens",
        sa.Column("token_id", sa.String(128), primary_key=True),
        sa.Column("execution_id", sa.String(64), nullable=False, index=True),
        sa.Column("step_id", sa.String(64), nullable=False),
        sa.Column("approval_id", sa.String(64), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("hrms_hitl_workflow_tokens")
    op.drop_table("hrms_saga_compensation_logs")
