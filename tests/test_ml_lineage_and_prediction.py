"""
Tests for Governed Prediction Inferences, Abstention, and Decision Lineage Audit Trails.
"""

from __future__ import annotations

import pytest

from backend.ml.domain.enums import PredictionDecision
from backend.ml.domain.models import ModelVersion, PredictionRequest, ThresholdPolicy
from backend.ml.inference.prediction_service import PredictionService
from backend.ml.lineage.lineage_service import DecisionLineageService
from backend.ml.registry.model_registry import ModelRegistryService


@pytest.mark.asyncio
async def test_governed_inference_and_lineage_recording():
    svc = PredictionService.get_instance()
    reg = ModelRegistryService.get_instance()
    lin_svc = DecisionLineageService.get_instance()

    org_id = "org-pred-test"

    # Register & activate model
    model = await reg.register_model(org_id, name="AttritionPredictorLive")
    v1 = ModelVersion(
        model_id=model.model_id,
        organization_id=org_id,
        version_number=1,
        algorithm="LogisticRegression",
        dataset_version_id="dsv-101",
        feature_set_version="1.0",
        storage_reference="ref",
    )
    await reg.store.save_version(v1)
    await reg.release_service.activate_model(org_id, model.model_id, v1.version_id, approved_by="admin")

    # Set threshold policy: abstain if confidence < 0.55
    policy = ThresholdPolicy(
        organization_id=org_id,
        model_id=model.model_id,
        decision_threshold=0.50,
        abstain_confidence_threshold=0.55,
    )
    await reg.store.save_threshold_policy(policy)

    # Valid inference request
    req = PredictionRequest(
        organization_id=org_id,
        model_id=model.model_id,
        actor_id="hr-user",
        actor_roles=["HR_MANAGER"],
        input_features={"employee_tenure_months": 24.0, "leave_frequency_90d": 5.0},
    )
    res = await svc.predict(req)

    assert res.decision == PredictionDecision.PREDICT
    assert res.model_version == 1
    assert res.confidence >= 0.50
    assert len(res.lineage_id) > 0

    # Verify decision lineage stored
    lineage = await lin_svc.get_lineage(org_id, res.lineage_id)
    assert lineage is not None
    assert lineage.model_id == model.model_id
    assert lineage.dataset_version == "dsv-101"
    assert lineage.correlation_id == req.correlation_id
    assert "employee_tenure_months" in lineage.input_feature_hashes

    # Connect real-world business outcome
    feedback = await lin_svc.record_outcome_feedback(
        organization_id=org_id,
        prediction_id=res.prediction_id,
        lineage_id=res.lineage_id,
        actual_outcome="EMPLOYEE_RETAINED_AFTER_1ON1",
        human_override=False,
    )
    assert feedback.actual_outcome == "EMPLOYEE_RETAINED_AFTER_1ON1"
