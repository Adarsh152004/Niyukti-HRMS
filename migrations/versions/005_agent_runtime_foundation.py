"""agent_runtime_foundation

Revision ID: 005_agent_runtime_foundation
Revises: 004_workflow_execution_tables
Create Date: 2026-08-23 11:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005_agent_runtime_foundation"
down_revision: Union[str, None] = "004_workflow_execution_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agents
    op.create_table(
        "agents",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("agent_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("capabilities_json", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("system_instructions_reference", sa.String(length=512), nullable=True),
        sa.Column("max_concurrent_tasks", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_agent_org_name"),
    )
    op.create_index("ix_agents_org_status", "agents", ["organization_id", "status"], unique=False)

    # 2. Agent Capabilities
    op.create_table(
        "agent_capabilities",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("capability_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("resource", sa.String(length=128), nullable=False),
        sa.Column("actions_json", sa.JSON(), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("requires_hitl", sa.Boolean(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_caps_agent_id", "agent_capabilities", ["agent_id"], unique=False)

    # 3. Agent Tasks
    op.create_table(
        "agent_tasks",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("parent_task_id", sa.String(length=64), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=False),
        sa.Column("goal", sa.String(length=512), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.String(length=512), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_tasks_org_agent", "agent_tasks", ["organization_id", "agent_id"], unique=False)
    op.create_index("ix_agent_tasks_status", "agent_tasks", ["status"], unique=False)
    op.create_index("ix_agent_tasks_corr_id", "agent_tasks", ["correlation_id"], unique=False)

    # 4. Agent Task Events
    op.create_table(
        "agent_task_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["agent_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_events_task_id", "agent_task_events", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_table("agent_task_events")
    op.drop_table("agent_tasks")
    op.drop_table("agent_capabilities")
    op.drop_table("agents")
