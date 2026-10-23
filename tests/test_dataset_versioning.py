"""
Tests for Dataset Versioning, Splitting, and Data Governance.
"""

from __future__ import annotations

import pytest

from backend.ml.datasets.dataset_service import DatasetService
from backend.ml.domain.exceptions import GovernanceCheckFailedError
from backend.ml.synthetic.generator import SyntheticHRDataGenerator


@pytest.mark.asyncio
async def test_dataset_creation_and_versioning():
    svc = DatasetService.get_instance()
    org_id = "org-ds-test"

    # Create dataset definition
    ds = await svc.create_dataset(
        organization_id=org_id,
        name="Attrition Training Dataset",
        target_column="will_attrite",
        feature_ids=["employee_tenure_months", "leave_frequency_90d", "attendance_rate_30d"],
    )
    assert ds.name == "Attrition Training Dataset"

    # Generate synthetic records
    records = SyntheticHRDataGenerator.generate_attrition_dataset(num_records=100, seed=101)

    # Create version
    ver, splits = await svc.create_dataset_version(
        organization_id=org_id,
        dataset_id=ds.dataset_id,
        rows=records,
        split_strategy="TEMPORAL",
        synthetic=True,
    )
    assert ver.version_number == 1
    assert ver.row_count == 100
    assert len(splits.train_data) == 70
    assert len(splits.val_data) == 15
    assert len(splits.test_data) == 15
    assert len(ver.checksum) == 64


def test_sensitive_feature_governance_block():
    svc = DatasetService.get_instance()
    # National ID is classified as RESTRICTED PII and must be blocked from dataset training features
    with pytest.raises(GovernanceCheckFailedError):
        svc.verify_training_data_governance(["national_id", "leave_frequency_90d"])
