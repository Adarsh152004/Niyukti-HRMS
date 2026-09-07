"""
Dataset Store Port — Contract for dataset metadata and partition persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.ml.domain.models import DatasetDefinition, DatasetVersion


class DatasetStorePort(ABC):
    """Abstraction for dataset definition and version metadata persistence."""

    @abstractmethod
    async def save_dataset(self, dataset: DatasetDefinition) -> DatasetDefinition: ...

    @abstractmethod
    async def get_dataset(self, organization_id: str, dataset_id: str) -> DatasetDefinition | None: ...

    @abstractmethod
    async def list_datasets(self, organization_id: str) -> Sequence[DatasetDefinition]: ...

    @abstractmethod
    async def save_version(self, version: DatasetVersion) -> DatasetVersion: ...

    @abstractmethod
    async def get_version(self, organization_id: str, version_id: str) -> DatasetVersion | None: ...

    @abstractmethod
    async def list_versions(self, organization_id: str, dataset_id: str) -> Sequence[DatasetVersion]: ...
