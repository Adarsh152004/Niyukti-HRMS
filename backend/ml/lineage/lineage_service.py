"""
Decision Lineage Service — Audits the complete provenance graph for every prediction and real-world outcome.
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Sequence
from typing import Any

from backend.ml.domain.enums import PredictionDecision
from backend.ml.domain.models import OutcomeFeedback, PredictionLineage
from backend.ml.infrastructure.in_memory import InMemoryLineageStore
from backend.ml.ports.model_storage import LineageStorePort

logger = logging.getLogger(__name__)


class DecisionLineageService:
    """Records and serves immutable lineage trees linking predictions, datasets, features, policies, and outcomes."""

    _instance: DecisionLineageService | None = None

    def __init__(self, lineage_store: LineageStorePort | None = None) -> None:
        self.store = lineage_store or InMemoryLineageStore.get_instance()
        self._outcomes: dict[str, OutcomeFeedback] = {}

    @classmethod
    def get_instance(cls) -> DecisionLineageService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def hash_features(features: dict[str, Any]) -> dict[str, str]:
        """Hash feature values to preserve lineage without exposing raw sensitive data in audit records."""
        hashed: dict[str, str] = {}
        for k, v in features.items():
            val_str = str(v).encode("utf-8")
            hashed[k] = hashlib.sha256(val_str).hexdigest()[:16]
        return hashed

    async def record_prediction_lineage(
        self,
        organization_id: str,
        prediction_id: str,
        model_id: str,
        model_version: int,
        feature_set_version: str,
        dataset_version: str,
        input_features: dict[str, Any],
        decision: PredictionDecision,
        confidence: float,
        correlation_id: str,
        threshold_policy_version: int = 1,
        governance_policy_version: str = "1.0",
    ) -> PredictionLineage:
        """Create and persist an immutable prediction lineage node."""
        feature_hashes = self.hash_features(input_features)

        lineage = PredictionLineage(
            organization_id=organization_id,
            prediction_id=prediction_id,
            model_id=model_id,
            model_version=model_version,
            feature_set_version=feature_set_version,
            dataset_version=dataset_version,
            threshold_policy_version=threshold_policy_version,
            governance_policy_version=governance_policy_version,
            input_feature_hashes=feature_hashes,
            decision=decision,
            confidence=confidence,
            correlation_id=correlation_id,
        )

        return await self.store.save_lineage(lineage)

    async def get_lineage(self, organization_id: str, lineage_id: str) -> PredictionLineage | None:
        return await self.store.get_lineage(organization_id, lineage_id)

    async def list_model_lineages(self, organization_id: str, model_id: str, limit: int = 50) -> Sequence[PredictionLineage]:
        return await self.store.list_lineages_for_model(organization_id, model_id, limit=limit)

    async def record_outcome_feedback(
        self,
        organization_id: str,
        prediction_id: str,
        lineage_id: str,
        actual_outcome: Any,
        human_override: bool = False,
        human_decision_notes: str = "",
    ) -> OutcomeFeedback:
        """Connect prediction lineage to real-world ground truth for ongoing feedback loops."""
        feedback = OutcomeFeedback(
            organization_id=organization_id,
            prediction_id=prediction_id,
            lineage_id=lineage_id,
            actual_outcome=actual_outcome,
            human_override=human_override,
            human_decision_notes=human_decision_notes,
        )
        self._outcomes[feedback.feedback_id] = feedback
        logger.info(f"Recorded business outcome for prediction [{prediction_id}]: {actual_outcome}")
        return feedback
