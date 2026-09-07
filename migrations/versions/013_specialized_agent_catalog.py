"""Specialized Agent Catalog and Policy Binding Tables

Revision ID: 013_specialized_agent_catalog
Revises: 012_ml_platform
Create Date: 2026-08-30 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "013_specialized_agent_catalog"
down_revision = "012_ml_platform"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Specialized Agent Definitions ──────────────────────────────────────
    op.create_table(
        "specialized_agent_definitions",
        sa.Column("role", sa.String(64), primary_key=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("responsibilities", sa.JSON(), nullable=False, default=list),
        sa.Column("supervisor_role", sa.String(64), nullable=True),
        sa.Column("autonomy_mode", sa.String(32), nullable=False, default="SUPERVISED"),
        sa.Column("version", sa.String(32), nullable=False, default="1.0.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("daily_budget_usd", sa.Float(), nullable=False, default=5.0),
        sa.Column("max_execution_time_seconds", sa.Integer(), nullable=False, default=120),
        sa.Column("max_tool_calls_per_task", sa.Integer(), nullable=False, default=15),
        sa.Column("max_delegation_depth", sa.Integer(), nullable=False, default=2),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── 2. Specialized Agent Instances (Tenant Bound) ─────────────────────────
    op.create_table(
        "specialized_agent_instances",
        sa.Column("instance_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("role", sa.String(64), nullable=False, index=True),
        sa.Column("agent_id", sa.String(64), nullable=False, index=True),
        sa.Column("actor_id", sa.String(64), nullable=False, index=True),
        sa.Column("definition_version", sa.String(32), nullable=False),
        sa.Column("autonomy_mode", sa.String(32), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, default=True),
        sa.Column("custom_parameters", sa.JSON(), nullable=False, default=dict),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── 3. Agent Capability Bindings ──────────────────────────────────────────
    op.create_table(
        "agent_capability_bindings",
        sa.Column("binding_id", sa.String(64), primary_key=True),
        sa.Column("role", sa.String(64), nullable=False, index=True),
        sa.Column("capability_token", sa.String(128), nullable=False, index=True),
        sa.Column("is_prohibited", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── 4. Agent Tool Bindings ────────────────────────────────────────────────
    op.create_table(
        "agent_tool_bindings",
        sa.Column("binding_id", sa.String(64), primary_key=True),
        sa.Column("role", sa.String(64), nullable=False, index=True),
        sa.Column("tool_id", sa.String(128), nullable=False, index=True),
        sa.Column("access_level", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── 5. Agent Evaluation Contracts ─────────────────────────────────────────
    op.create_table(
        "agent_evaluation_contracts",
        sa.Column("contract_id", sa.String(64), primary_key=True),
        sa.Column("role", sa.String(64), nullable=False, unique=True),
        sa.Column("accuracy_metric", sa.String(128), nullable=False),
        sa.Column("min_accuracy_score", sa.Float(), nullable=False),
        sa.Column("max_hallucination_rate", sa.Float(), nullable=False),
        sa.Column("unauthorized_retrieval_limit", sa.Integer(), nullable=False, default=0),
        sa.Column("target_sla_seconds", sa.Integer(), nullable=False),
        sa.Column("evaluation_criteria", sa.JSON(), nullable=False, default=list),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("agent_evaluation_contracts")
    op.drop_table("agent_tool_bindings")
    op.drop_table("agent_capability_bindings")
    op.drop_table("specialized_agent_instances")
    op.drop_table("specialized_agent_definitions")
