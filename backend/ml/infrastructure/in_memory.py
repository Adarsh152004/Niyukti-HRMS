"""
In-Memory implementations of FeatureStore, DatasetStore, ModelRegistry, and LineageStore.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

from backend.ml.domain.enums import ModelStage
from backend.ml.domain.models import (
    DatasetDefinition,
    DatasetVersion,
    FeatureDefinition,
    ModelDefinition,
    ModelVersion,
    PredictionLineage,
    ThresholdPolicy,
)
from backend.ml.ports.dataset_store import DatasetStorePort
from backend.ml.ports.feature_store import FeatureStorePort
from backend.ml.ports.model_storage import LineageStorePort, ModelRegistryPort


class InMemoryFeatureStore(FeatureStorePort):
    """In-memory FeatureStore supporting definition registration and online entity vector serving."""

    _instance: InMemoryFeatureStore | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._definitions: dict[str, FeatureDefinition] = {}
        # Key: (organization_id, entity_id) -> {feature_name: value}
        self._online_vectors: dict[tuple[str, str], dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> InMemoryFeatureStore:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def register_feature(self, feature: FeatureDefinition) -> FeatureDefinition:
        async with self._lock:
            self._definitions[feature.name] = feature
            return feature

    async def get_feature(self, feature_name: str) -> FeatureDefinition | None:
        async with self._lock:
            return self._definitions.get(feature_name)

    async def list_features(self) -> Sequence[FeatureDefinition]:
        async with self._lock:
            return list(self._definitions.values())

    async def save_online_features(
        self,
        organization_id: str,
        entity_id: str,
        features: dict[str, Any],
    ) -> None:
        async with self._lock:
            key = (organization_id, entity_id)
            if key not in self._online_vectors:
                self._online_vectors[key] = {}
            self._online_vectors[key].update(features)

    async def get_online_features(
        self,
        organization_id: str,
        entity_id: str,
        feature_names: Sequence[str],
    ) -> dict[str, Any]:
        async with self._lock:
            key = (organization_id, entity_id)
            vector = self._online_vectors.get(key, {})
            return {f: vector.get(f) for f in feature_names}


class InMemoryDatasetStore(DatasetStorePort):
    """In-memory DatasetStore for dataset definitions and immutable version records."""

    _instance: InMemoryDatasetStore | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._datasets: dict[str, DatasetDefinition] = {}
        self._versions: dict[str, DatasetVersion] = {}

    @classmethod
    def get_instance(cls) -> InMemoryDatasetStore:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def save_dataset(self, dataset: DatasetDefinition) -> DatasetDefinition:
        async with self._lock:
            self._datasets[dataset.dataset_id] = dataset
            return dataset

    async def get_dataset(self, organization_id: str, dataset_id: str) -> DatasetDefinition | None:
        async with self._lock:
            d = self._datasets.get(dataset_id)
            if d and d.organization_id == organization_id:
                return d
            return None

    async def list_datasets(self, organization_id: str) -> Sequence[DatasetDefinition]:
        async with self._lock:
            return [d for d in self._datasets.values() if d.organization_id == organization_id]

    async def save_version(self, version: DatasetVersion) -> DatasetVersion:
        async with self._lock:
            self._versions[version.version_id] = version
            return version

    async def get_version(self, organization_id: str, version_id: str) -> DatasetVersion | None:
        async with self._lock:
            v = self._versions.get(version_id)
            if v and v.organization_id == organization_id:
                return v
            return None

    async def list_versions(self, organization_id: str, dataset_id: str) -> Sequence[DatasetVersion]:
        async with self._lock:
            return [v for v in self._versions.values() if v.organization_id == organization_id and v.dataset_id == dataset_id]


class InMemoryModelRegistry(ModelRegistryPort):
    """In-memory ModelRegistry for catalog, versions, and threshold policies."""

    _instance: InMemoryModelRegistry | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._models: dict[str, ModelDefinition] = {}
        self._versions: dict[str, ModelVersion] = {}
        self._threshold_policies: dict[tuple[str, str], ThresholdPolicy] = {}

    @classmethod
    def get_instance(cls) -> InMemoryModelRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def save_model(self, model: ModelDefinition) -> ModelDefinition:
        async with self._lock:
            self._models[model.model_id] = model
            return model

    async def get_model(self, organization_id: str, model_id: str) -> ModelDefinition | None:
        async with self._lock:
            m = self._models.get(model_id)
            if m and m.organization_id == organization_id:
                return m
            return None

    async def list_models(self, organization_id: str, stage: ModelStage | None = None) -> Sequence[ModelDefinition]:
        async with self._lock:
            res = [m for m in self._models.values() if m.organization_id == organization_id]
            if stage:
                res = [m for m in res if m.stage == stage]
            return res

    async def save_version(self, version: ModelVersion) -> ModelVersion:
        async with self._lock:
            self._versions[version.version_id] = version
            return version

    async def get_version(self, organization_id: str, version_id: str) -> ModelVersion | None:
        async with self._lock:
            v = self._versions.get(version_id)
            if v and v.organization_id == organization_id:
                return v
            return None

    async def list_versions(self, organization_id: str, model_id: str) -> Sequence[ModelVersion]:
        async with self._lock:
            return [v for v in self._versions.values() if v.organization_id == organization_id and v.model_id == model_id]

    async def save_threshold_policy(self, policy: ThresholdPolicy) -> ThresholdPolicy:
        async with self._lock:
            self._threshold_policies[(policy.organization_id, policy.model_id)] = policy
            return policy

    async def get_threshold_policy(self, organization_id: str, model_id: str) -> ThresholdPolicy | None:
        async with self._lock:
            return self._threshold_policies.get((organization_id, model_id))


class InMemoryLineageStore(LineageStorePort):
    """In-memory LineageStore for immutable decision audit graph."""

    _instance: InMemoryLineageStore | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._lineages: dict[str, PredictionLineage] = {}

    @classmethod
    def get_instance(cls) -> InMemoryLineageStore:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def save_lineage(self, lineage: PredictionLineage) -> PredictionLineage:
        async with self._lock:
            self._lineages[lineage.lineage_id] = lineage
            return lineage

    async def get_lineage(self, organization_id: str, lineage_id: str) -> PredictionLineage | None:
        async with self._lock:
            lin = self._lineages.get(lineage_id)
            if lin and lin.organization_id == organization_id:
                return lin
            return None

    async def list_lineages_for_model(self, organization_id: str, model_id: str, limit: int = 50) -> Sequence[PredictionLineage]:
        async with self._lock:
            records = [
                lin for lin in self._lineages.values() if lin.organization_id == organization_id and lin.model_id == model_id
            ]
            return sorted(records, key=lambda x: x.created_at, reverse=True)[:limit]
