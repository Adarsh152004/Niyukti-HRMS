"""
Training Service — End-to-end model training, validation, multi-paradigm evaluation, and ModelCard generation.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from backend.ml.datasets.dataset_service import DatasetService
from backend.ml.domain.enums import ModelStage, ModelType
from backend.ml.domain.models import (
    ModelCard,
    ModelVersion,
)
from backend.ml.evaluation.calibration import ProbabilityCalibrationEvaluator
from backend.ml.evaluation.fairness import FairnessEvaluator
from backend.ml.evaluation.metrics import ModelMetricsCalculator
from backend.ml.infrastructure.in_memory import InMemoryModelRegistry
from backend.ml.ports.model_storage import ModelRegistryPort
from backend.ml.training.baselines import BaselineClassifier, BaselineRegressor
from backend.runtime.events import EventBus

logger = logging.getLogger(__name__)


class TrainingService:
    """Orchestrates model training, evaluation, fairness audits, and registry staging."""

    def __init__(
        self,
        model_registry: ModelRegistryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.registry = model_registry or InMemoryModelRegistry.get_instance()
        self.event_bus = event_bus or EventBus.get_instance()
        self.dataset_service = DatasetService.get_instance()

    async def train_model_candidate(
        self,
        organization_id: str,
        model_id: str,
        dataset_version_id: str,
        feature_names: Sequence[str],
        target_column: str,
        train_data: list[dict[str, Any]],
        val_data: list[dict[str, Any]],
        algorithm: str = "LogisticRegression",
        hyperparameters: dict[str, Any] | None = None,
        protected_attribute_name: str | None = None,
        model_type: ModelType = ModelType.CLASSIFICATION,
    ) -> ModelVersion:
        """
        Full Training Pipeline:
        1. Fit model on training split.
        2. Evaluate on validation split (accuracy, precision, recall, F1, AUC / MAE, RMSE).
        3. Perform probability calibration analysis (Brier, ECE).
        4. Execute post-hoc fairness evaluation on protected attribute if provided.
        5. Generate comprehensive ModelCard.
        6. Persist ModelVersion candidate in DEVELOPMENT stage.
        """
        hp = hyperparameters or {"epochs": 25, "lr": 0.05}

        metrics: dict[str, float] = {}
        calib_metrics: dict[str, float] = {}
        fairness_metrics: dict[str, float] = {}

        if model_type == ModelType.CLASSIFICATION:
            model = BaselineClassifier(feature_names=feature_names)
            model.fit(train_data, target_column=target_column, epochs=hp.get("epochs", 25), lr=hp.get("lr", 0.05))

            # Validate
            y_true = [int(r.get(target_column, 0)) for r in val_data]
            y_prob = [model.predict_proba(r) for r in val_data]
            y_pred = [1 if p >= 0.50 else 0 for p in y_prob]

            # 1. Performance Metrics
            metrics = ModelMetricsCalculator.classification_metrics(y_true, y_pred, y_prob)

            # 2. Calibration
            cal_res = ProbabilityCalibrationEvaluator.evaluate_calibration(y_true, y_prob)
            calib_metrics = {
                "brier_score": cal_res.brier_score,
                "expected_calibration_error": cal_res.expected_calibration_error,
            }

            # 3. Fairness
            if protected_attribute_name:
                protected_groups = [str(r.get(protected_attribute_name, "default")) for r in val_data]
                fair_rep = FairnessEvaluator.evaluate_fairness(
                    organization_id=organization_id,
                    model_id=model_id,
                    model_version_id="temp",
                    protected_attribute_name=protected_attribute_name,
                    protected_groups=protected_groups,
                    y_true=y_true,
                    y_pred=y_pred,
                )
                fairness_metrics = {
                    "demographic_parity_difference": fair_rep.demographic_parity_difference,
                    "equal_opportunity_difference": fair_rep.equal_opportunity_difference,
                    "disparate_impact_ratio": fair_rep.disparate_impact_ratio,
                    "is_compliant": 1.0 if fair_rep.is_compliant else 0.0,
                }

        else:
            reg_model = BaselineRegressor(feature_names=feature_names)
            reg_model.fit(train_data, target_column=target_column, epochs=hp.get("epochs", 25), lr=hp.get("lr", 0.01))

            y_true_reg = [float(r.get(target_column, 0.0)) for r in val_data]
            y_pred_reg = [reg_model.predict(r) for r in val_data]
            metrics = ModelMetricsCalculator.regression_metrics(y_true_reg, y_pred_reg)

        # 4. Construct ModelCard
        model_card = ModelCard(
            purpose=f"Predictive {model_type.value} model for HR intelligence",
            intended_users=["HR Managers", "Talent Operations", "Autonomous HR Agents"],
            prohibited_uses=["Autonomous employee termination", "Autonomous salary cuts without HITL approval"],
            target_demographics="Tenant employees",
            training_data_summary=f"Trained on {len(train_data)} records, validated on {len(val_data)} records",
            features_used=list(feature_names),
            ethical_considerations=["Must not be used for fully automated consequential employment actions."],
            known_limitations=["Baseline linear reference model; requires domain calibration."],
            evaluation_summary=metrics,
            fairness_summary=fairness_metrics,
            human_in_the_loop_requirements="High-risk decisions (>0.80) require explicit human approval.",
        )

        existing_versions = await self.registry.list_versions(organization_id, model_id)
        next_ver = len(existing_versions) + 1

        version_rec = ModelVersion(
            model_id=model_id,
            organization_id=organization_id,
            version_number=next_ver,
            algorithm=algorithm,
            dataset_version_id=dataset_version_id,
            feature_set_version="1.0",
            hyperparameters=hp,
            storage_reference=f"storage://{organization_id}/models/{model_id}/v{next_ver}",
            stage=ModelStage.DEVELOPMENT,
            model_card=model_card,
            metrics=metrics,
            fairness_metrics=fairness_metrics,
            calibration_metrics=calib_metrics,
            is_governance_approved=False,
        )

        saved = await self.registry.save_version(version_rec)
        logger.info(f"Trained and registered model version {next_ver} for model [{model_id}]")
        return saved
