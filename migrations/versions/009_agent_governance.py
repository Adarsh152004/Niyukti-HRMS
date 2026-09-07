"""Agent Governance, Budgets, Execution Ledger, Violations and Evaluation tables.

Revision ID: 009_agent_governance
Revises: 008_agent_delegation
Create Date: 2026-08-24 19:35:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009_agent_governance"
down_revision: Union[str, None] = "008_agent_delegation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. agent_governance_policies
    op.create_table(
        "agent_governance_policies",
        sa.Column("policy_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("governance_state", sa.String(length=32), nullable=False, server_default="ACTIVE"),
        sa.Column("max_reasoning_steps_per_task", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("max_tool_calls_per_task", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("max_delegation_depth", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("max_concurrent_tasks", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("allowed_tool_categories", sa.JSON(), nullable=True),
        sa.Column("prohibited_tool_categories", sa.JSON(), nullable=True),
        sa.Column("auto_quarantine_on_violation", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("policy_id"),
        sa.UniqueConstraint("organization_id", "agent_id", name="uq_agent_governance_policy_tenant_agent"),
    )

    # 2. agent_budgets
    op.create_table(
        "agent_budgets",
        sa.Column("budget_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("max_token_budget", sa.Integer(), nullable=False, server_default="100000"),
        sa.Column("tokens_consumed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_reasoning_runs", sa.Integer(), nullable=False, server_default="500"),
        sa.Column("reasoning_runs_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_tool_calls", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("tool_calls_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_command_executions", sa.Integer(), nullable=False, server_default="500"),
        sa.Column("command_executions_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_delegated_tasks", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("delegated_tasks_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("budget_id"),
        sa.UniqueConstraint("organization_id", "agent_id", name="uq_agent_budget_tenant_agent"),
    )

    # 3. agent_execution_ledger
    op.create_table(
        "agent_execution_ledger",
        sa.Column("ledger_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("resource", sa.String(length=128), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False, server_default="LOW"),
        sa.Column("decision", sa.String(length=32), nullable=False, server_default="ALLOWED"),
        sa.Column("policy_result", sa.String(length=32), nullable=False, server_default="SUCCESS"),
        sa.Column("authorization_result", sa.String(length=32), nullable=False, server_default="AUTHORIZED"),
        sa.Column("approval_result", sa.String(length=32), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("causation_id", sa.String(length=128), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("ledger_id"),
    )
    op.create_index("idx_ledger_org_agent", "agent_execution_ledger", ["organization_id", "agent_id"])

    # 4. agent_governance_violations
    op.create_table(
        "agent_governance_violations",
        sa.Column("violation_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=True),
        sa.Column("violation_type", sa.String(length=64), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="HIGH"),
        sa.Column("action_taken", sa.String(length=64), nullable=False, server_default="LOGGED"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("violation_id"),
    )

    # 5. agent_evaluations
    op.create_table(
        "agent_evaluations",
        sa.Column("evaluation_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("evaluator", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("criteria_evaluated", sa.JSON(), nullable=True),
        sa.Column("failures", sa.JSON(), nullable=True),
        sa.Column("warnings", sa.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("evaluation_id"),
    )


def downgrade() -> None:
    op.drop_table("agent_evaluations")
    op.drop_table("agent_governance_violations")
    op.drop_index("idx_ledger_org_agent", table_name="agent_execution_ledger")
    op.drop_table("agent_execution_ledger")
    op.drop_table("agent_budgets")
    op.drop_table("agent_governance_policies")
