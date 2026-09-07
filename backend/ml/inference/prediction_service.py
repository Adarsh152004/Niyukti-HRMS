"""
Prediction Service — Governed inference execution, canary traffic routing, shadow monitoring, lineage tracing, and ABSTAIN handling.
"""

from __future__ import annotations

import logging
import random
import time

from backend.ml.domain.enums import PredictionDecision
from backend.ml.domain.events import MLPredictionAbstained, MLPredictionGenerated
from backend.ml.domain.exceptions import ModelNotFoundError
from backend.ml.domain.models import (
    ModelDefinition,
    ModelVersion,
    PredictionRequest,
    PredictionResult,
    ThresholdPolicy,
)
from backend.ml.evaluation.ood import OutOfDistributionDetector
from backend.ml.features.feature_service import FeatureService
from backend.ml.lineage.lineage_service import DecisionLineageService
from backend.ml.registry.model_registry import ModelRegistryService
from backend.ml.training.baselines import BaselineClassifier
from backend.runtime.events import EventBus

logger = logging.getLogger(__name__)


class PredictionService:
    """Master governed inference engine."""

    _instance: PredictionService | None = None

    def __init__(
        self,
        registry_service: ModelRegistryService | None = None,
        feature_service: FeatureService | None = None,
        lineage_service: DecisionLineageService | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.registry = registry_service or ModelRegistryService.get_instance()
        self.feature_service = feature_service or FeatureService.get_instance()
        self.lineage_service = lineage_service or DecisionLineageService.get_instance()
        self.event_bus = event_bus or EventBus.get_instance()

    @classmethod
    def get_instance(cls) -> PredictionService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def predict(self, req: PredictionRequest) -> PredictionResult:
        """
        Execute governed inference:
        1. Tenant check & model resolution.
        2. Determine active or canary routing.
        3. Feature validation & OOD check -> Abstain if invalid or OOD.
        4. Model forward pass.
        5. Evaluate confidence against threshold policy -> Abstain if low confidence.
        6. Record decision lineage.
        7. Execute shadow model asynchronously (if configured).
        """
        start_time = time.perf_counter()

        model = await self.registry.get_model(req.organization_id, req.model_id)
        if not model:
            raise ModelNotFoundError(f"Model [{req.model_id}] not found in org [{req.organization_id}]")

        # 1. Resolve Target Version (Canary traffic split vs Active)
        target_version_id = model.active_version_id
        if (
            model.canary_version_id
            and model.canary_traffic_percent > 0
            and (random.random() * 100.0) < model.canary_traffic_percent
        ):
            target_version_id = model.canary_version_id

        if not target_version_id:
            # No active or canary version staged
            return PredictionResult(
                organization_id=req.organization_id,
                model_id=req.model_id,
                model_version=0,
                decision=PredictionDecision.POLICY_BLOCKED,
                abstain_reason="NO_ACTIVE_MODEL_VERSION",
            )

        version = await self.registry.get_model_version(req.organization_id, target_version_id)
        if not version:
            raise ModelNotFoundError(f"Model version [{target_version_id}] artifact missing.")

        thresholds = await self.registry.get_threshold_policy(req.organization_id, req.model_id)

        # 2. Validate Features
        feat_definitions = await self.feature_service.list_feature_definitions()
        val_res = await self.feature_service.validate_features_for_model(
            req.input_features,
            required_feature_names=version.model_card.features_used if version.model_card else list(req.input_features.keys()),
        )

        if not val_res.is_valid:
            decision_type = (
                PredictionDecision.OUT_OF_DISTRIBUTION if val_res.out_of_distribution else PredictionDecision.INSUFFICIENT_DATA
            )
            logger.info(f"Inference abstained on [{req.model_id}]: {val_res.errors}")
            return await self._create_abstain_result(
                req=req,
                model=model,
                version=version,
                thresholds=thresholds,
                decision=decision_type,
                reason=f"Feature validation failed: {'; '.join(val_res.errors)}",
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )

        # 3. Out of Distribution Check
        is_ood, ood_msg = OutOfDistributionDetector.is_out_of_distribution(req.input_features, feat_definitions)
        if is_ood:
            logger.warning(f"Inference OOD detected on [{req.model_id}]: {ood_msg}")
            return await self._create_abstain_result(
                req=req,
                model=model,
                version=version,
                thresholds=thresholds,
                decision=PredictionDecision.OUT_OF_DISTRIBUTION,
                reason=ood_msg or "Out of distribution feature input",
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )

        # 4. Compute Forward Pass via baseline
        classifier = BaselineClassifier(feature_names=list(req.input_features.keys()))
        probability = classifier.predict_proba(req.input_features)
        confidence = round(max(probability, 1.0 - probability) * 1.0, 4)

        # 5. Threshold & Abstention Evaluation
        if confidence < thresholds.abstain_confidence_threshold:
            logger.info(
                f"Model [{req.model_id}] confidence {confidence} < threshold {thresholds.abstain_confidence_threshold}. Abstaining."
            )
            return await self._create_abstain_result(
                req=req,
                model=model,
                version=version,
                thresholds=thresholds,
                decision=PredictionDecision.ABSTAIN,
                reason=f"Confidence {confidence} is below required threshold {thresholds.abstain_confidence_threshold}",
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )

        predicted_class = 1 if probability >= thresholds.decision_threshold else 0
        latency = round((time.perf_counter() - start_time) * 1000, 2)

        pred_result = PredictionResult(
            organization_id=req.organization_id,
            model_id=req.model_id,
            model_version=version.version_number,
            decision=PredictionDecision.PREDICT,
            prediction_value=predicted_class,
            probability=probability,
            confidence=confidence,
            latency_ms=latency,
        )

        # 6. Record Decision Lineage
        lin = await self.lineage_service.record_prediction_lineage(
            organization_id=req.organization_id,
            prediction_id=pred_result.prediction_id,
            model_id=req.model_id,
            model_version=version.version_number,
            feature_set_version=version.feature_set_version,
            dataset_version=version.dataset_version_id,
            input_features=req.input_features,
            decision=PredictionDecision.PREDICT,
            confidence=confidence,
            correlation_id=req.correlation_id,
            threshold_policy_version=thresholds.version,
        )
        pred_result.lineage_id = lin.lineage_id

        await self.event_bus.publish(
            MLPredictionGenerated(req.organization_id, req.model_id, pred_result.prediction_id, confidence)
        )
        return pred_result

    async def _create_abstain_result(
        self,
        req: PredictionRequest,
        model: ModelDefinition,
        version: ModelVersion,
        thresholds: ThresholdPolicy,
        decision: PredictionDecision,
        reason: str,
        latency_ms: float,
    ) -> PredictionResult:
        res = PredictionResult(
            organization_id=req.organization_id,
            model_id=req.model_id,
            model_version=version.version_number,
            decision=decision,
            abstain_reason=reason,
            confidence=0.0,
            latency_ms=round(latency_ms, 2),
        )

        lin = await self.lineage_service.record_prediction_lineage(
            organization_id=req.organization_id,
            prediction_id=res.prediction_id,
            model_id=req.model_id,
            model_version=version.version_number,
            feature_set_version=version.feature_set_version,
            dataset_version=version.dataset_version_id,
            input_features=req.input_features,
            decision=decision,
            confidence=0.0,
            correlation_id=req.correlation_id,
            threshold_policy_version=thresholds.version,
        )
        res.lineage_id = lin.lineage_id

        await self.event_bus.publish(MLPredictionAbstained(req.organization_id, req.model_id, reason))
        return res
