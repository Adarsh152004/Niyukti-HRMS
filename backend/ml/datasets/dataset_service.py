"""
Dataset Service & Governance — Manages dataset creation, versioning, and privacy governance compliance.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Sequence
from typing import Any

from backend.ml.datasets.split_service import DatasetSplitResult, DatasetSplitService
from backend.ml.domain.exceptions import GovernanceCheckFailedError
from backend.ml.domain.models import DatasetDefinition, DatasetVersion
from backend.ml.infrastructure.in_memory import InMemoryDatasetStore
from backend.ml.ports.dataset_store import DatasetStorePort
from backend.privacy.classification import SENSITIVE_FIELDS_MAP
from backend.security.pii import PIIClassification

logger = logging.getLogger(__name__)


class DatasetService:
    """Orchestrates dataset lifecycle, versioning, splitting, and data privacy governance."""

    _instance: DatasetService | None = None

    def __init__(self, dataset_store: DatasetStorePort | None = None) -> None:
        self.store = dataset_store or InMemoryDatasetStore.get_instance()

    @classmethod
    def get_instance(cls) -> DatasetService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def verify_training_data_governance(feature_names: Sequence[str]) -> None:
        """
        Governance invariant: Ensure no HIGHLY_SENSITIVE/RESTRICTED PII fields
        (passwords, national IDs, bank details) are used as raw model features.
        """
        for f in feature_names:
            cls = SENSITIVE_FIELDS_MAP.get(f)
            if cls in [PIIClassification.HIGHLY_SENSITIVE, PIIClassification.RESTRICTED]:
                raise GovernanceCheckFailedError(
                    f"Feature '{f}' is classified as {cls.value} and cannot be used in training datasets."
                )

    async def create_dataset(
        self,
        organization_id: str,
        name: str,
        target_column: str,
        feature_ids: list[str],
        owner: str = "data-science",
        description: str = "",
    ) -> DatasetDefinition:
        """Register a logical dataset definition."""
        self.verify_training_data_governance(feature_ids)

        ds = DatasetDefinition(
            organization_id=organization_id,
            name=name,
            description=description,
            feature_ids=feature_ids,
            target_column=target_column,
            owner=owner,
        )
        return await self.store.save_dataset(ds)

    async def create_dataset_version(
        self,
        organization_id: str,
        dataset_id: str,
        rows: list[dict[str, Any]],
        split_strategy: str = "TEMPORAL",
        synthetic: bool = False,
    ) -> tuple[DatasetVersion, DatasetSplitResult]:
        """
        Create an immutable version of a dataset:
        1. Compute SHA-256 checksum of raw payload.
        2. Partition into train/val/test splits.
        3. Persist version metadata.
        """
        raw_bytes = json.dumps(rows, sort_keys=True).encode("utf-8")
        checksum = hashlib.sha256(raw_bytes).hexdigest()

        # Split data
        if split_strategy == "TEMPORAL":
            splits = DatasetSplitService.temporal_split(rows)
        elif split_strategy == "ENTITY_GROUPED":
            splits = DatasetSplitService.entity_grouped_split(rows)
        else:
            splits = DatasetSplitService.random_split(rows)

        existing_versions = await self.store.list_versions(organization_id, dataset_id)
        next_ver = len(existing_versions) + 1

        version_rec = DatasetVersion(
            dataset_id=dataset_id,
            organization_id=organization_id,
            version_number=next_ver,
            row_count=len(rows),
            checksum=checksum,
            storage_reference=f"storage://{organization_id}/datasets/{dataset_id}/v{next_ver}",
            split_strategy=split_strategy,
            train_rows=len(splits.train_data),
            val_rows=len(splits.val_data),
            test_rows=len(splits.test_data),
            pii_purged=True,
            synthetic=synthetic,
        )

        saved = await self.store.save_version(version_rec)
        logger.info(f"Created dataset version {next_ver} for dataset [{dataset_id}] with {len(rows)} rows.")
        return saved, splits
