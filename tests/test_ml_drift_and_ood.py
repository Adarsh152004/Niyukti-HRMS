"""
Tests for Model Drift Detection and Out-of-Distribution (OOD) Abstention.
"""

from __future__ import annotations

import pytest

from backend.ml.domain.enums import DriftSeverity, PredictionDecision
from backend.ml.domain.models import FeatureDefinition, ModelVersion, PredictionRequest
from backend.ml.evaluation.drift import DriftDetector
from backend.ml.evaluation.ood import OutOfDistributionDetector
from backend.ml.inference.prediction_service import PredictionService
from backend.ml.registry.model_registry import ModelRegistryService


def test_drift_detector_severity():
    baseline = [10.0, 10.2, 9.8, 10.1, 9.9]
    # Small shift -> NONE
    rep_none = DriftDetector.evaluate_numeric_drift(
        organization_id="org-1",
        model_id="mdl-1",
        model_version_id="v1",
        feature_name="tenure",
        baseline_values=baseline,
        current_values=[10.05, 10.15, 9.95],
    )
    assert rep_none.severity in [DriftSeverity.NONE, DriftSeverity.LOW]

    # Extreme shift -> CRITICAL
    rep_crit = DriftDetector.evaluate_numeric_drift(
        organization_id="org-1",
        model_id="mdl-1",
        model_version_id="v1",
        feature_name="tenure",
        baseline_values=baseline,
        current_values=[50.0, 55.0, 60.0],
    )
    assert rep_crit.severity == DriftSeverity.CRITICAL
    assert rep_crit.drift_score > 2.0


def test_ood_detector():
    defs = [
        FeatureDefinition(
            name="tenure", source_table="t", transformation_logic="raw", owner="dev", min_value=0.0, max_value=120.0
        ),
        FeatureDefinition(
            name="attendance", source_table="t", transformation_logic="raw", owner="dev", min_value=0.0, max_value=1.0
        ),
    ]

    # In-distribution
    is_ood, _ = OutOfDistributionDetector.is_out_of_distribution({"tenure": 24.0, "attendance": 0.9}, defs)
    assert is_ood is False

    # Negative attendance -> OOD
    is_ood_neg, reason = OutOfDistributionDetector.is_out_of_distribution({"tenure": 24.0, "attendance": -0.5}, defs)
    assert is_ood_neg is True
    assert "below minimum" in reason


@pytest.mark.asyncio
async def test_prediction_abstains_on_ood():
    svc = PredictionService.get_instance()
    reg = ModelRegistryService.get_instance()
    org_id = "org-ood-test"

    model = await reg.register_model(org_id, name="TestOODModel")
    v1 = ModelVersion(
        model_id=model.model_id,
        organization_id=org_id,
        version_number=1,
        algorithm="LR",
        dataset_version_id="dsv-1",
        feature_set_version="1.0",
        storage_reference="ref",
    )
    await reg.store.save_version(v1)
    await reg.release_service.activate_model(org_id, model.model_id, v1.version_id, approved_by="admin")

    # Pass OOD feature value (e.g. employee tenure 10,000 months)
    req = PredictionRequest(
        organization_id=org_id,
        model_id=model.model_id,
        actor_id="emp-1",
        actor_roles=["HR_ADMIN"],
        input_features={"employee_tenure_months": 10000.0, "leave_frequency_90d": 2},
    )
    res = await svc.predict(req)
    assert res.decision == PredictionDecision.OUT_OF_DISTRIBUTION
    assert "max_value" in res.abstain_reason or "maximum" in res.abstain_reason
