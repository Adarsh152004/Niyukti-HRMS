"""
Model Registry Service — Central catalog for models, immutable versions, model cards, and threshold policies.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.ml.domain.enums import ModelStage, ModelType
from backend.ml.domain.events import MLModelRegistered
from backend.ml.domain.models import (
    ModelDefinition,
    ModelVersion,
    ThresholdPolicy,
)
from backend.ml.infrastructure.in_memory import InMemoryModelRegistry
from backend.ml.ports.model_storage import ModelRegistryPort
from backend.ml.registry.release_service import ModelReleaseService
from backend.ml.registry.rollback_service import ModelRollbackService
from backend.runtime.events import EventBus

logger = logging.getLogger(__name__)


class ModelRegistryService:
    """Master service controller for the Model Registry and Lifecycle."""

    _instance: ModelRegistryService | None = None

    def __init__(
        self,
        registry_port: ModelRegistryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.store = registry_port or InMemoryModelRegistry.get_instance()
        self.event_bus = event_bus or EventBus.get_instance()
        self.release_service = ModelReleaseService(registry=self.store, event_bus=self.event_bus)
        self.rollback_service = ModelRollbackService(registry=self.store, event_bus=self.event_bus)

    @classmethod
    def get_instance(cls) -> ModelRegistryService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def register_model(
        self,
        organization_id: str,
        name: str,
        model_type: ModelType = ModelType.CLASSIFICATION,
        description: str = "",
        owner: str = "ml-platform",
    ) -> ModelDefinition:
        """Register a new logical model entity."""
        model = ModelDefinition(
            organization_id=organization_id,
            name=name,
            model_type=model_type,
            description=description,
            owner=owner,
            stage=ModelStage.DEVELOPMENT,
        )
        saved = await self.store.save_model(model)
        # Configure default threshold policy
        policy = ThresholdPolicy(organization_id=organization_id, model_id=saved.model_id)
        await self.store.save_threshold_policy(policy)

        await self.event_bus.publish(MLModelRegistered(organization_id, saved.model_id, name))
        return saved

    async def get_model(self, organization_id: str, model_id: str) -> ModelDefinition | None:
        return await self.store.get_model(organization_id, model_id)

    async def list_models(self, organization_id: str, stage: ModelStage | None = None) -> Sequence[ModelDefinition]:
        return await self.store.list_models(organization_id, stage=stage)

    async def get_model_version(self, organization_id: str, version_id: str) -> ModelVersion | None:
        return await self.store.get_version(organization_id, version_id)

    async def list_model_versions(self, organization_id: str, model_id: str) -> Sequence[ModelVersion]:
        return await self.store.list_versions(organization_id, model_id)

    async def get_threshold_policy(self, organization_id: str, model_id: str) -> ThresholdPolicy:
        policy = await self.store.get_threshold_policy(organization_id, model_id)
        if not policy:
            policy = ThresholdPolicy(organization_id=organization_id, model_id=model_id)
            await self.store.save_threshold_policy(policy)
        return policy
