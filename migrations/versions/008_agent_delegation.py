"""agent_delegation

Revision ID: 008_agent_delegation
Revises: 007_agent_orchestration
Create Date: 2026-08-24 19:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "008_agent_delegation"
down_revision: Union[str, None] = "007_agent_orchestration"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agent Delegations Table
    op.create_table(
        "agent_delegations",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("delegator_agent_id", sa.String(length=64), nullable=False),
        sa.Column("delegate_agent_id", sa.String(length=64), nullable=False),
        sa.Column("parent_task_id", sa.String(length=64), nullable=False),
        sa.Column("delegated_task_id", sa.String(length=64), nullable=True),
        sa.Column("capabilities_json", sa.JSON(), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("parent_delegation_id", sa.String(length=64), nullable=True),
        sa.Column("allow_further_delegation", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("payload_hash", sa.String(length=128), nullable=True),
        sa.Column("rejection_reason", sa.String(length=512), nullable=True),
        sa.Column("revocation_reason", sa.String(length=512), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_delegations_org_id", "agent_delegations", ["organization_id"])
    op.create_index("ix_agent_delegations_delegator", "agent_delegations", ["delegator_agent_id"])
    op.create_index("ix_agent_delegations_delegate", "agent_delegations", ["delegate_agent_id"])
    op.create_index("ix_agent_delegations_status", "agent_delegations", ["status"])
    op.create_index("ix_agent_delegations_expires_at", "agent_delegations", ["expires_at"])
    op.create_index("ix_agent_delegations_correlation_id", "agent_delegations", ["correlation_id"])

    # 2. Agent Delegated Tasks Table
    op.create_table(
        "agent_delegated_tasks",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("delegation_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("delegator_agent_id", sa.String(length=64), nullable=False),
        sa.Column("delegate_agent_id", sa.String(length=64), nullable=False),
        sa.Column("goal", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("failure_reason", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["delegation_id"], ["agent_delegations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_delegated_tasks_delegation_id", "agent_delegated_tasks", ["delegation_id"])
    op.create_index("ix_agent_delegated_tasks_org_id", "agent_delegated_tasks", ["organization_id"])


def downgrade() -> None:
    op.drop_table("agent_delegated_tasks")
    op.drop_table("agent_delegations")
