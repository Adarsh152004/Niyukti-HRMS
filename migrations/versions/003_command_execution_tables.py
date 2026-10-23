"""command_execution_tables

Revision ID: 003_command_execution_tables
Revises: 002_security_tables
Create Date: 2026-08-22 21:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_command_execution_tables"
down_revision: Union[str, None] = "002_security_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Commands
    op.create_table(
        "commands",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("command_type", sa.String(length=128), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("payload_hash", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "idempotency_key", name="uq_cmd_org_idempotency"),
    )
    op.create_index("ix_cmd_org_type", "commands", ["organization_id", "command_type"], unique=False)

    # 2. Command Executions
    op.create_table(
        "command_executions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("command_id", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("error", sa.String(length=512), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=False),
        sa.Column("executor", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["command_id"], ["commands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cmd_exec_cmd_id", "command_executions", ["command_id"], unique=False)

    # 3. Command Approvals
    op.create_table(
        "command_approvals",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("command_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("requested_by_actor_id", sa.String(length=64), nullable=False),
        sa.Column("approver_actor_id", sa.String(length=64), nullable=True),
        sa.Column("payload_hash", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=512), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["command_id"], ["commands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cmd_appr_org_status", "command_approvals", ["organization_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_table("command_approvals")
    op.drop_table("command_executions")
    op.drop_table("commands")
