"""
Tests for Model Training Pipeline and ModelVersion Candidate Packaging.
"""

from __future__ import annotations

import pytest

from backend.ml.datasets.dataset_service import DatasetService
from backend.ml.domain.enums import ModelStage, ModelType
from backend.ml.registry.model_registry import ModelRegistryService
from backend.ml.synthetic.generator import SyntheticHRDataGenerator
from backend.ml.training.training_service import TrainingService


@pytest.mark.asyncio
async def test_end_to_end_model_training_and_staging():
    reg = ModelRegistryService.get_instance()
    ds_svc = DatasetService.get_instance()
    train_svc = TrainingService(model_registry=reg.store)

    org_id = "org-train-test"

    # 1. Register logical model
    model = await reg.register_model(
        organization_id=org_id,
        name="EmployeeAttritionModel",
        model_type=ModelType.CLASSIFICATION,
    )

    # 2. Create dataset version
    ds = await ds_svc.create_dataset(
        organization_id=org_id,
        name="DS_Attrition",
        target_column="will_attrite",
        feature_ids=["employee_tenure_months", "leave_frequency_90d", "attendance_rate_30d"],
    )
    records = SyntheticHRDataGenerator.generate_attrition_dataset(num_records=150, seed=42)
    dsv, splits = await ds_svc.create_dataset_version(
        organization_id=org_id,
        dataset_id=ds.dataset_id,
        rows=records,
    )

    # 3. Train Model Version Candidate
    version_candidate = await train_svc.train_model_candidate(
        organization_id=org_id,
        model_id=model.model_id,
        dataset_version_id=dsv.version_id,
        feature_names=["employee_tenure_months", "leave_frequency_90d", "attendance_rate_30d"],
        target_column="will_attrite",
        train_data=splits.train_data,
        val_data=splits.val_data,
        protected_attribute_name="gender",
        model_type=ModelType.CLASSIFICATION,
    )

    assert version_candidate.version_number == 1
    assert version_candidate.stage == ModelStage.DEVELOPMENT
    assert "accuracy" in version_candidate.metrics
    assert "brier_score" in version_candidate.calibration_metrics
    assert "demographic_parity_difference" in version_candidate.fairness_metrics
    assert version_candidate.model_card is not None
