"""
ML Domain Enums — Life-cycle stages, model paradigms, decision types, feature types, and fairness metrics.
"""

from __future__ import annotations

from enum import StrEnum


class ModelType(StrEnum):
    """Machine learning operational paradigms."""

    CLASSIFICATION = "CLASSIFICATION"
    REGRESSION = "REGRESSION"
    RANKING = "RANKING"
    FORECASTING = "FORECASTING"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    CLUSTERING = "CLUSTERING"


class ModelStage(StrEnum):
    """Governed lifecycle release stages."""

    DEVELOPMENT = "DEVELOPMENT"
    EVALUATION = "EVALUATION"
    SHADOW = "SHADOW"
    CANARY = "CANARY"
    ACTIVE = "ACTIVE"
    RESTRICTED = "RESTRICTED"
    RETIRED = "RETIRED"
    ROLLED_BACK = "ROLLED_BACK"


class PredictionDecision(StrEnum):
    """Deterministic prediction disposition."""

    PREDICT = "PREDICT"
    ABSTAIN = "ABSTAIN"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    OUT_OF_DISTRIBUTION = "OUT_OF_DISTRIBUTION"
    POLICY_BLOCKED = "POLICY_BLOCKED"


class FeatureDataType(StrEnum):
    """Feature primitive datatypes."""

    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    BOOLEAN = "BOOLEAN"
    DATETIME = "DATETIME"
    TEXT = "TEXT"
    VECTOR = "VECTOR"


class FeatureSensitivity(StrEnum):
    """Sensitivity classification for features."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    SENSITIVE = "SENSITIVE"
    PROTECTED_ATTRIBUTE = "PROTECTED_ATTRIBUTE"  # e.g. age, gender (used only for post-hoc fairness evaluation)
    RESTRICTED = "RESTRICTED"


class DatasetSplitType(StrEnum):
    """Dataset partition strategies."""

    TRAIN = "TRAIN"
    VALIDATION = "VALIDATION"
    TEST = "TEST"
    HOLDOUT = "HOLDOUT"


class DriftSeverity(StrEnum):
    """Drift magnitude categories."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FairnessMetricType(StrEnum):
    """Algorithmic fairness evaluation metrics."""

    DEMOGRAPHIC_PARITY_DIFFERENCE = "DEMOGRAPHIC_PARITY_DIFFERENCE"
    EQUAL_OPPORTUNITY_DIFFERENCE = "EQUAL_OPPORTUNITY_DIFFERENCE"
    EQUALIZED_ODDS = "EQUALIZED_ODDS"
    DISPARATE_IMPACT_RATIO = "DISPARATE_IMPACT_RATIO"
    FALSE_POSITIVE_RATE_DIFFERENCE = "FALSE_POSITIVE_RATE_DIFFERENCE"
