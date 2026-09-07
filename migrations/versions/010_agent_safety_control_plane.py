"""Agent Safety Control Plane: Policies, Audit Records, Metrics, Anomalies, and Containment Actions tables.

Revision ID: 010_agent_safety_control_plane
Revises: 009_agent_governance
Create Date: 2026-08-26 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010_agent_safety_control_plane"
down_revision: Union[str, None] = "009_agent_governance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. agent_safety_policies
    op.create_table(
        "agent_safety_policies",
        sa.Column("policy_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False, server_default="Safety Policy"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("governance_state", sa.String(length=32), nullable=False, server_default="ACTIVE"),
        sa.Column("rules", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("policy_id"),
    )
    op.create_index("idx_safety_pol_org_agent", "agent_safety_policies", ["organization_id", "agent_id"])

    # 2. agent_audit_records
    op.create_table(
        "agent_audit_records",
        sa.Column("audit_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=True),
        sa.Column("execution_id", sa.String(length=64), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("resource", sa.String(length=128), nullable=False),
        sa.Column("tool_name", sa.String(length=128), nullable=True),
        sa.Column("command_name", sa.String(length=128), nullable=True),
        sa.Column("risk_level", sa.String(length=32), nullable=False, server_default="LOW"),
        sa.Column("policy_result", sa.String(length=32), nullable=False, server_default="SUCCESS"),
        sa.Column("authorization_result", sa.String(length=32), nullable=False, server_default="AUTHORIZED"),
        sa.Column("approval_required", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("approval_status", sa.String(length=32), nullable=True),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("audit_id"),
    )
    op.create_index("idx_audit_rec_org_agent", "agent_audit_records", ["organization_id", "agent_id"])
    op.create_index("idx_audit_rec_corr", "agent_audit_records", ["correlation_id"])

    # 3. agent_metrics
    op.create_table(
        "agent_metrics",
        sa.Column("metric_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=True),
        sa.Column("metric_name", sa.String(length=128), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("dimensions", sa.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("metric_id"),
    )
    op.create_index("idx_metrics_org_name", "agent_metrics", ["organization_id", "metric_name"])

    # 4. agent_anomalies
    op.create_table(
        "agent_anomalies",
        sa.Column("anomaly_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=True),
        sa.Column("anomaly_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="MEDIUM"),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.8"),
        sa.Column("evidence", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="OPEN"),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("anomaly_id"),
    )
    op.create_index("idx_anomalies_org_agent", "agent_anomalies", ["organization_id", "agent_id"])

    # 5. agent_containment_actions
    op.create_table(
        "agent_containment_actions",
        sa.Column("containment_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("agent_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("triggered_by", sa.String(length=64), nullable=False),
        sa.Column("previous_status", sa.String(length=32), nullable=False),
        sa.Column("resulting_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("containment_id"),
    )
    op.create_index("idx_containment_org_agent", "agent_containment_actions", ["organization_id", "agent_id"])


def downgrade() -> None:
    op.drop_index("idx_containment_org_agent", table_name="agent_containment_actions")
    op.drop_table("agent_containment_actions")
    op.drop_index("idx_anomalies_org_agent", table_name="agent_anomalies")
    op.drop_table("agent_anomalies")
    op.drop_index("idx_metrics_org_name", table_name="agent_metrics")
    op.drop_table("agent_metrics")
    op.drop_index("idx_audit_rec_corr", table_name="agent_audit_records")
    op.drop_index("idx_audit_rec_org_agent", table_name="agent_audit_records")
    op.drop_table("agent_audit_records")
    op.drop_index("idx_safety_pol_org_agent", table_name="agent_safety_policies")
    op.drop_table("agent_safety_policies")
