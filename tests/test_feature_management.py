"""
Tests for Feature Definitions, Validation, and Online FeatureStore Serving.
"""

from __future__ import annotations

import pytest

from backend.ml.domain.enums import FeatureDataType
from backend.ml.domain.models import FeatureDefinition
from backend.ml.features.feature_service import FeatureService
from backend.ml.features.feature_validation import FeatureValidator


@pytest.mark.asyncio
async def test_feature_service_and_store():
    svc = FeatureService.get_instance()
    await svc.initialize_standard_features()

    feat = await svc.get_feature_definition("employee_tenure_months")
    assert feat is not None
    assert feat.datatype == FeatureDataType.NUMERIC

    # Store and retrieve online entity feature vector
    org_id = "org-feat-test"
    emp_id = "emp-001"
    vector = {
        "employee_tenure_months": 24.5,
        "leave_frequency_90d": 3,
        "attendance_rate_30d": 0.96,
    }
    await svc.store_entity_features(org_id, emp_id, vector)

    retrieved = await svc.get_entity_features(org_id, emp_id, ["employee_tenure_months", "leave_frequency_90d"])
    assert retrieved["employee_tenure_months"] == 24.5
    assert retrieved["leave_frequency_90d"] == 3


def test_feature_validator_bounds_and_missingness():
    defs = [
        FeatureDefinition(
            name="tenure", source_table="t", transformation_logic="raw", owner="dev", min_value=0.0, max_value=120.0
        ),
        FeatureDefinition(
            name="attendance", source_table="t", transformation_logic="raw", owner="dev", min_value=0.0, max_value=1.0
        ),
    ]

    # Valid vector
    v_valid = {"tenure": 24.0, "attendance": 0.95}
    res_valid = FeatureValidator.validate_vector(v_valid, defs)
    assert res_valid.is_valid is True
    assert res_valid.out_of_distribution is False

    # Out of distribution (exceeds max bound)
    v_ood = {"tenure": 500.0, "attendance": 0.95}
    res_ood = FeatureValidator.validate_vector(v_ood, defs)
    assert res_ood.is_valid is False
    assert res_ood.out_of_distribution is True

    # Missing required feature
    v_missing = {"tenure": 12.0}
    res_missing = FeatureValidator.validate_vector(v_missing, defs)
    assert res_missing.is_valid is False
    assert "attendance" in res_missing.missing_required_features
