"""
ML Domain Models — Definitions for Features, Datasets, Models, Experiments, Fairness, Drift, Lineage, and Inferences.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.ml.domain.enums import (
    DriftSeverity,
    FeatureDataType,
    FeatureSensitivity,
    ModelStage,
    ModelType,
    PredictionDecision,
)


class FeatureDefinition(BaseModel):
    """Declarative specification for an engineered HR feature."""

    feature_id: str = Field(default_factory=lambda: f"feat-{uuid.uuid4()}")
    name: str = Field(description="Unique snake_case identifier e.g. 'leave_frequency_90d'")
    description: str = Field(default="")
    datatype: FeatureDataType = Field(default=FeatureDataType.NUMERIC)
    source_table: str = Field(description="HRMS source entity e.g. 'leaves'")
    transformation_logic: str = Field(description="Specification of calculation")
    sensitivity: FeatureSensitivity = Field(default=FeatureSensitivity.INTERNAL)
    owner: str = Field(description="Team or author")
    version: int = Field(default=1)
    freshness_sla_seconds: int = Field(default=86400, description="Max allowed staleness")
    min_value: float | None = None
    max_value: float | None = None
    allowed_categories: list[str] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class FeatureVersion(BaseModel):
    """Immutable snapshot of feature definition."""

    feature_id: str
    version_number: int
    definition_hash: str
    feature_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class DatasetDefinition(BaseModel):
    """Metadata container for an ML training / evaluation dataset."""

    dataset_id: str = Field(default_factory=lambda: f"ds-{uuid.uuid4()}")
    organization_id: str = Field(description="Tenant isolation boundary")
    name: str
    description: str = ""
    feature_ids: list[str] = Field(default_factory=list)
    target_column: str
    owner: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class DatasetVersion(BaseModel):
    """Immutable versioned dataset artifact."""

    version_id: str = Field(default_factory=lambda: f"dsv-{uuid.uuid4()}")
    dataset_id: str
    organization_id: str
    version_number: int
    row_count: int
    checksum: str = Field(description="SHA-256 hash of dataset content")
    schema_version: str = "1.0"
    feature_set_version: str = "1.0"
    storage_reference: str
    split_strategy: str = "TEMPORAL"  # or STRATIFIED / RANDOM
    train_rows: int = 0
    val_rows: int = 0
    test_rows: int = 0
    pii_purged: bool = True
    synthetic: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class ThresholdPolicy(BaseModel):
    """Versioned decision and abstention boundaries for a model."""

    policy_id: str = Field(default_factory=lambda: f"thresh-{uuid.uuid4()}")
    organization_id: str
    model_id: str
    version: int = 1
    decision_threshold: float = 0.50
    abstain_confidence_threshold: float = 0.60
    alert_high_risk_threshold: float = 0.80
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class ModelCard(BaseModel):
    """Responsible AI transparency documentation for ML models."""

    purpose: str
    intended_users: list[str]
    prohibited_uses: list[str]
    target_demographics: str
    training_data_summary: str
    features_used: list[str]
    ethical_considerations: list[str]
    known_limitations: list[str]
    evaluation_summary: dict[str, float] = Field(default_factory=dict)
    fairness_summary: dict[str, float] = Field(default_factory=dict)
    human_in_the_loop_requirements: str


class ModelDefinition(BaseModel):
    """Logical model registry entity."""

    model_id: str = Field(default_factory=lambda: f"mdl-{uuid.uuid4()}")
    organization_id: str = Field(description="Tenant isolation boundary")
    name: str = Field(description="Human-readable model name e.g. 'AttritionPredictor'")
    description: str = ""
    model_type: ModelType = Field(default=ModelType.CLASSIFICATION)
    current_version: int = 1
    stage: ModelStage = Field(default=ModelStage.DEVELOPMENT)
    owner: str = Field(default="ml-platform")
    active_version_id: str | None = None
    shadow_version_id: str | None = None
    canary_version_id: str | None = None
    canary_traffic_percent: float = 0.0
    rollback_target_version_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    activated_at: datetime | None = None
    retired_at: datetime | None = None


class ModelVersion(BaseModel):
    """Immutable trained model snapshot with artifacts and evaluation scores."""

    version_id: str = Field(default_factory=lambda: f"mver-{uuid.uuid4()}")
    model_id: str
    organization_id: str
    version_number: int
    algorithm: str = Field(description="e.g. 'LogisticRegression', 'RandomForest'")
    dataset_version_id: str
    feature_set_version: str
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    storage_reference: str
    stage: ModelStage = Field(default=ModelStage.DEVELOPMENT)
    model_card: ModelCard | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
    fairness_metrics: dict[str, float] = Field(default_factory=dict)
    calibration_metrics: dict[str, float] = Field(default_factory=dict)
    is_governance_approved: bool = False
    approved_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class Experiment(BaseModel):
    """Training run / hyperparameter search record."""

    experiment_id: str = Field(default_factory=lambda: f"exp-{uuid.uuid4()}")
    organization_id: str
    model_id: str
    dataset_version_id: str
    algorithm: str
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    status: str = "COMPLETED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class FairnessReport(BaseModel):
    """Audited evaluation of disparate impact and demographic parity."""

    report_id: str = Field(default_factory=lambda: f"fair-{uuid.uuid4()}")
    organization_id: str
    model_id: str
    model_version_id: str
    protected_attribute: str
    demographic_parity_difference: float
    equal_opportunity_difference: float
    disparate_impact_ratio: float
    is_compliant: bool
    threshold_applied: float = 0.10
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class DriftReport(BaseModel):
    """Feature or prediction drift evaluation."""

    report_id: str = Field(default_factory=lambda: f"drift-{uuid.uuid4()}")
    organization_id: str
    model_id: str
    model_version_id: str
    feature_name: str
    drift_score: float  # e.g. Kolmogorov-Smirnov statistic or PSI
    severity: DriftSeverity = Field(default=DriftSeverity.NONE)
    baseline_mean: float
    current_mean: float
    baseline_missing_rate: float
    current_missing_rate: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class PredictionRequest(BaseModel):
    """Unified inference request."""

    organization_id: str
    model_id: str
    actor_id: str
    actor_roles: list[str]
    input_features: dict[str, Any]
    entity_id: str | None = None  # e.g. employee_id or applicant_id
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4()}")


class PredictionResult(BaseModel):
    """Unified governed inference response."""

    prediction_id: str = Field(default_factory=lambda: f"pred-{uuid.uuid4()}")
    organization_id: str
    model_id: str
    model_version: int
    decision: PredictionDecision
    prediction_value: Any = None  # Class label, numeric score, or ranking list
    probability: float | None = None
    confidence: float = 0.0
    abstain_reason: str | None = None
    feature_attributions: dict[str, float] = Field(default_factory=dict)
    latency_ms: float = 0.0
    lineage_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class PredictionLineage(BaseModel):
    """Immutable audit record linking prediction to underlying datasets and policies."""

    lineage_id: str = Field(default_factory=lambda: f"lin-{uuid.uuid4()}")
    organization_id: str
    prediction_id: str
    model_id: str
    model_version: int
    feature_set_version: str
    dataset_version: str
    preprocessing_version: str = "1.0"
    threshold_policy_version: int = 1
    governance_policy_version: str = "1.0"
    input_feature_hashes: dict[str, str] = Field(default_factory=dict)
    decision: PredictionDecision
    confidence: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    correlation_id: str


class OutcomeFeedback(BaseModel):
    """Real-world ground truth feedback linking prediction to business outcome."""

    feedback_id: str = Field(default_factory=lambda: f"feed-{uuid.uuid4()}")
    organization_id: str
    prediction_id: str
    lineage_id: str
    actual_outcome: Any
    human_override: bool = False
    human_decision_notes: str = ""
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
