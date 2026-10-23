"""
Tests for Algorithmic Fairness Auditing and Deployment Gates.
"""

from __future__ import annotations

import pytest

from backend.ml.domain.enums import ModelStage
from backend.ml.domain.exceptions import GovernanceCheckFailedError
from backend.ml.domain.models import ModelVersion
from backend.ml.evaluation.fairness import FairnessEvaluator
from backend.ml.governance.deployment_gate import MLDeploymentGate
from backend.ml.registry.model_registry import ModelRegistryService


def test_fairness_evaluator_demographic_parity():
    groups = ["A", "A", "A", "A", "B", "B", "B", "B"]
    y_true = [1, 1, 0, 0, 1, 0, 0, 0]
    y_pred = [1, 1, 0, 0, 1, 0, 0, 0]

    report = FairnessEvaluator.evaluate_fairness(
        organization_id="org-1",
        model_id="mdl-1",
        model_version_id="v1",
        protected_attribute_name="gender",
        protected_groups=groups,
        y_true=y_true,
        y_pred=y_pred,
        max_allowed_parity_gap=0.30,
    )
    # Selection rate Group A = 2/4 = 0.50, Group B = 1/4 = 0.25 -> gap = 0.25 <= 0.30
    assert report.demographic_parity_difference == 0.25
    assert report.is_compliant is True


def test_deployment_gate_evaluation():
    # Compliant version
    ver_ok = ModelVersion(
        model_id="mdl-1",
        organization_id="org-1",
        version_number=1,
        algorithm="LR",
        dataset_version_id="dsv-1",
        feature_set_version="1.0",
        storage_reference="ref",
        metrics={"accuracy": 0.85},
        calibration_metrics={"expected_calibration_error": 0.08},
        fairness_metrics={"demographic_parity_difference": 0.05, "is_compliant": 1.0},
    )
    res_ok = MLDeploymentGate.evaluate_gate(ver_ok)
    assert res_ok.is_approved is True

    # Failed fairness gap
    ver_biased = ModelVersion(
        model_id="mdl-2",
        organization_id="org-1",
        version_number=1,
        algorithm="LR",
        dataset_version_id="dsv-1",
        feature_set_version="1.0",
        storage_reference="ref",
        metrics={"accuracy": 0.85},
        calibration_metrics={"expected_calibration_error": 0.08},
        fairness_metrics={"demographic_parity_difference": 0.35, "is_compliant": 0.0},
    )
    res_biased = MLDeploymentGate.evaluate_gate(ver_biased)
    assert res_biased.is_approved is False
    assert res_biased.fairness_passed is False


@pytest.mark.asyncio
async def test_activation_blocked_on_fairness_failure():
    reg = ModelRegistryService.get_instance()
    org_id = "org-gate-test"

    model = await reg.register_model(org_id, name="CandidateScreeningModel")

    # Save biased version
    biased_ver = ModelVersion(
        model_id=model.model_id,
        organization_id=org_id,
        version_number=1,
        algorithm="LR",
        dataset_version_id="dsv-1",
        feature_set_version="1.0",
        storage_reference="ref",
        stage=ModelStage.DEVELOPMENT,
        fairness_metrics={"demographic_parity_difference": 0.40, "is_compliant": 0.0},
    )
    await reg.store.save_version(biased_ver)

    # Attempt activation -> MUST raise GovernanceCheckFailedError
    with pytest.raises(GovernanceCheckFailedError):
        await reg.release_service.activate_model(
            organization_id=org_id,
            model_id=model.model_id,
            version_id=biased_ver.version_id,
            approved_by="hr-admin",
        )
