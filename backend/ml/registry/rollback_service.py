"""
Model Rollback Service — Rapid and audited reversion of faulty production models.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from backend.ml.domain.enums import ModelStage
from backend.ml.domain.events import MLModelRolledBack
from backend.ml.domain.exceptions import ModelNotFoundError, ModelStageTransitionError
from backend.ml.domain.models import ModelDefinition
from backend.ml.ports.model_storage import ModelRegistryPort
from backend.runtime.events import EventBus

logger = logging.getLogger(__name__)


class ModelRollbackService:
    """Safely and reversibly rolls back active production models."""

    def __init__(
        self,
        registry: ModelRegistryPort,
        event_bus: EventBus | None = None,
    ) -> None:
        self.registry = registry
        self.event_bus = event_bus or EventBus.get_instance()

    async def rollback_model(
        self,
        organization_id: str,
        model_id: str,
        reason: str,
        operator_id: str,
    ) -> ModelDefinition:
        """Rollback active model to rollback_target_version_id without deleting any history."""
        model = await self.registry.get_model(organization_id, model_id)
        if not model:
            raise ModelNotFoundError(f"Model [{model_id}] not found.")

        target_version_id = model.rollback_target_version_id
        if not target_version_id:
            raise ModelStageTransitionError(f"No rollback target version configured for model [{model_id}].")

        target_version = await self.registry.get_version(organization_id, target_version_id)
        if not target_version:
            raise ModelNotFoundError(f"Target rollback version [{target_version_id}] not found.")

        # Mark current active as ROLLED_BACK
        if model.active_version_id:
            current_active = await self.registry.get_version(organization_id, model.active_version_id)
            if current_active:
                current_active.stage = ModelStage.ROLLED_BACK
                await self.registry.save_version(current_active)

        # Restore target version to ACTIVE
        target_version.stage = ModelStage.ACTIVE
        await self.registry.save_version(target_version)

        now = datetime.now(tz=UTC)
        model.active_version_id = target_version_id
        model.stage = ModelStage.ACTIVE
        model.updated_at = now
        model.canary_version_id = None
        model.canary_traffic_percent = 0.0

        saved = await self.registry.save_model(model)

        await self.event_bus.publish(MLModelRolledBack(organization_id, model_id, target_version_id, reason=reason))
        logger.warning(f"AUDIT: Model [{model_id}] rolled back to version [{target_version_id}] by [{operator_id}]: {reason}")
        return saved
