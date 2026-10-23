"""Predictive ML Platform and Decision Lineage Tables

Revision ID: 012_ml_platform
Revises: 011_knowledge_brain_and_memory_hierarchy
Create Date: 2026-08-27 17:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "012_ml_platform"
down_revision = "011_knowledge_brain_and_memory_hierarchy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. ML Models ──────────────────────────────────────────────────────────
    op.create_table(
        "ml_models",
        sa.Column("model_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("model_type", sa.String(64), nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False, default=1),
        sa.Column("stage", sa.String(32), nullable=False, default="DEVELOPMENT"),
        sa.Column("owner", sa.String(64), nullable=False),
        sa.Column("active_version_id", sa.String(64), nullable=True),
        sa.Column("shadow_version_id", sa.String(64), nullable=True),
        sa.Column("canary_version_id", sa.String(64), nullable=True),
        sa.Column("canary_traffic_percent", sa.Float(), nullable=False, default=0.0),
        sa.Column("rollback_target_version_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── 2. ML Model Versions ──────────────────────────────────────────────────
    op.create_table(
        "ml_model_versions",
        sa.Column("version_id", sa.String(64), primary_key=True),
        sa.Column("model_id", sa.String(64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("algorithm", sa.String(128), nullable=False),
        sa.Column("dataset_version_id", sa.String(64), nullable=False),
        sa.Column("feature_set_version", sa.String(32), nullable=False),
        sa.Column("hyperparameters", sa.JSON(), nullable=False, default=dict),
        sa.Column("storage_reference", sa.String(512), nullable=False),
        sa.Column("stage", sa.String(32), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False, default=dict),
        sa.Column("fairness_metrics", sa.JSON(), nullable=False, default=dict),
        sa.Column("calibration_metrics", sa.JSON(), nullable=False, default=dict),
        sa.Column("is_governance_approved", sa.Boolean(), nullable=False, default=False),
        sa.Column("approved_by", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── 3. ML Feature Definitions ─────────────────────────────────────────────
    op.create_table(
        "ml_feature_definitions",
        sa.Column("feature_id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("datatype", sa.String(32), nullable=False),
        sa.Column("source_table", sa.String(64), nullable=False),
        sa.Column("transformation_logic", sa.Text(), nullable=False),
        sa.Column("sensitivity", sa.String(32), nullable=False),
        sa.Column("owner", sa.String(64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, default=1),
        sa.Column("freshness_sla_seconds", sa.Integer(), nullable=False, default=86400),
        sa.Column("min_value", sa.Float(), nullable=True),
        sa.Column("max_value", sa.Float(), nullable=True),
        sa.Column("allowed_categories", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── 4. ML Datasets ────────────────────────────────────────────────────────
    op.create_table(
        "ml_datasets",
        sa.Column("dataset_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("feature_ids", sa.JSON(), nullable=False, default=list),
        sa.Column("target_column", sa.String(64), nullable=False),
        sa.Column("owner", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── 5. ML Dataset Versions ────────────────────────────────────────────────
    op.create_table(
        "ml_dataset_versions",
        sa.Column("version_id", sa.String(64), primary_key=True),
        sa.Column("dataset_id", sa.String(64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("storage_reference", sa.String(512), nullable=False),
        sa.Column("split_strategy", sa.String(32), nullable=False),
        sa.Column("train_rows", sa.Integer(), nullable=False, default=0),
        sa.Column("val_rows", sa.Integer(), nullable=False, default=0),
        sa.Column("test_rows", sa.Integer(), nullable=False, default=0),
        sa.Column("pii_purged", sa.Boolean(), nullable=False, default=True),
        sa.Column("synthetic", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── 6. ML Decision Lineage ────────────────────────────────────────────────
    op.create_table(
        "ml_prediction_lineage",
        sa.Column("lineage_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("prediction_id", sa.String(64), nullable=False, index=True),
        sa.Column("model_id", sa.String(64), nullable=False, index=True),
        sa.Column("model_version", sa.Integer(), nullable=False),
        sa.Column("feature_set_version", sa.String(32), nullable=False),
        sa.Column("dataset_version", sa.String(64), nullable=False),
        sa.Column("preprocessing_version", sa.String(32), nullable=False),
        sa.Column("threshold_policy_version", sa.Integer(), nullable=False),
        sa.Column("governance_policy_version", sa.String(32), nullable=False),
        sa.Column("input_feature_hashes", sa.JSON(), nullable=False, default=dict),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("correlation_id", sa.String(64), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── 7. ML Threshold Policies ──────────────────────────────────────────────
    op.create_table(
        "ml_threshold_policies",
        sa.Column("policy_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("model_id", sa.String(64), nullable=False, index=True),
        sa.Column("version", sa.Integer(), nullable=False, default=1),
        sa.Column("decision_threshold", sa.Float(), nullable=False, default=0.50),
        sa.Column("abstain_confidence_threshold", sa.Float(), nullable=False, default=0.60),
        sa.Column("alert_high_risk_threshold", sa.Float(), nullable=False, default=0.80),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ml_threshold_policies")
    op.drop_table("ml_prediction_lineage")
    op.drop_table("ml_dataset_versions")
    op.drop_table("ml_datasets")
    op.drop_table("ml_feature_definitions")
    op.drop_table("ml_model_versions")
    op.drop_table("ml_models")
