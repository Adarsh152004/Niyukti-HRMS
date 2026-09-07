"""
ML Domain Events — Audited telemetry emitted on model lifecycle transitions and predictions.
"""

from __future__ import annotations

from typing import Any

from backend.runtime.events import Event


class MLModelRegistered(Event):
    def __init__(self, organization_id: str, model_id: str, model_name: str, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.model.registered",
            source="ml.registry",
            payload={"organization_id": organization_id, "model_id": model_id, "model_name": model_name, **kwargs},
        )


class MLModelEvaluated(Event):
    def __init__(self, organization_id: str, model_id: str, version_id: str, metrics: dict[str, float], **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.model.evaluated",
            source="ml.evaluation",
            payload={
                "organization_id": organization_id,
                "model_id": model_id,
                "version_id": version_id,
                "metrics": metrics,
                **kwargs,
            },
        )


class MLModelPromotedToShadow(Event):
    def __init__(self, organization_id: str, model_id: str, version_id: str, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.model.promoted_to_shadow",
            source="ml.registry",
            payload={"organization_id": organization_id, "model_id": model_id, "version_id": version_id, **kwargs},
        )


class MLModelPromotedToCanary(Event):
    def __init__(self, organization_id: str, model_id: str, version_id: str, traffic_percent: float, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.model.promoted_to_canary",
            source="ml.registry",
            payload={
                "organization_id": organization_id,
                "model_id": model_id,
                "version_id": version_id,
                "traffic_percent": traffic_percent,
                **kwargs,
            },
        )


class MLModelActivated(Event):
    def __init__(self, organization_id: str, model_id: str, version_id: str, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.model.activated",
            source="ml.registry",
            payload={"organization_id": organization_id, "model_id": model_id, "version_id": version_id, **kwargs},
        )


class MLModelRestricted(Event):
    def __init__(self, organization_id: str, model_id: str, reason: str, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.model.restricted",
            source="ml.governance",
            payload={"organization_id": organization_id, "model_id": model_id, "reason": reason, **kwargs},
        )


class MLModelRolledBack(Event):
    def __init__(self, organization_id: str, model_id: str, target_version_id: str, reason: str, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.model.rolled_back",
            source="ml.rollback",
            payload={
                "organization_id": organization_id,
                "model_id": model_id,
                "target_version_id": target_version_id,
                "reason": reason,
                **kwargs,
            },
        )


class MLPredictionGenerated(Event):
    def __init__(self, organization_id: str, model_id: str, prediction_id: str, confidence: float, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.prediction.generated",
            source="ml.inference",
            payload={
                "organization_id": organization_id,
                "model_id": model_id,
                "prediction_id": prediction_id,
                "confidence": confidence,
                **kwargs,
            },
        )


class MLPredictionAbstained(Event):
    def __init__(self, organization_id: str, model_id: str, reason: str, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.prediction.abstained",
            source="ml.inference",
            payload={"organization_id": organization_id, "model_id": model_id, "reason": reason, **kwargs},
        )


class MLModelDriftDetected(Event):
    def __init__(
        self, organization_id: str, model_id: str, feature_name: str, drift_score: float, severity: str, **kwargs: Any
    ) -> None:
        super().__init__(
            event_type="ml.drift.detected",
            source="ml.monitoring",
            payload={
                "organization_id": organization_id,
                "model_id": model_id,
                "feature_name": feature_name,
                "drift_score": drift_score,
                "severity": severity,
                **kwargs,
            },
        )


class MLFairnessCheckFailed(Event):
    def __init__(self, organization_id: str, model_id: str, protected_attribute: str, gap: float, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.fairness.failed",
            source="ml.governance",
            payload={
                "organization_id": organization_id,
                "model_id": model_id,
                "protected_attribute": protected_attribute,
                "gap": gap,
                **kwargs,
            },
        )


class MLModelDeploymentBlocked(Event):
    def __init__(self, organization_id: str, model_id: str, reason: str, **kwargs: Any) -> None:
        super().__init__(
            event_type="ml.deployment.blocked",
            source="ml.governance",
            payload={"organization_id": organization_id, "model_id": model_id, "reason": reason, **kwargs},
        )
