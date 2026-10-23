"""
Model Storage and Registry Ports — Contract for model metadata, artifacts, versions, and lineage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.ml.domain.enums import ModelStage
from backend.ml.domain.models import (
    ModelDefinition,
    ModelVersion,
    PredictionLineage,
    ThresholdPolicy,
)


class ModelRegistryPort(ABC):
    """Abstraction for model catalog and version management."""

    @abstractmethod
    async def save_model(self, model: ModelDefinition) -> ModelDefinition: ...

    @abstractmethod
    async def get_model(self, organization_id: str, model_id: str) -> ModelDefinition | None: ...

    @abstractmethod
    async def list_models(self, organization_id: str, stage: ModelStage | None = None) -> Sequence[ModelDefinition]: ...

    @abstractmethod
    async def save_version(self, version: ModelVersion) -> ModelVersion: ...

    @abstractmethod
    async def get_version(self, organization_id: str, version_id: str) -> ModelVersion | None: ...

    @abstractmethod
    async def list_versions(self, organization_id: str, model_id: str) -> Sequence[ModelVersion]: ...

    @abstractmethod
    async def save_threshold_policy(self, policy: ThresholdPolicy) -> ThresholdPolicy: ...

    @abstractmethod
    async def get_threshold_policy(self, organization_id: str, model_id: str) -> ThresholdPolicy | None: ...


class LineageStorePort(ABC):
    """Abstraction for immutable decision lineage graph."""

    @abstractmethod
    async def save_lineage(self, lineage: PredictionLineage) -> PredictionLineage: ...

    @abstractmethod
    async def get_lineage(self, organization_id: str, lineage_id: str) -> PredictionLineage | None: ...

    @abstractmethod
    async def list_lineages_for_model(
        self, organization_id: str, model_id: str, limit: int = 50
    ) -> Sequence[PredictionLineage]: ...
