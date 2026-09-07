"""
Model Release Service — Manages promotions to SHADOW, CANARY (with traffic ramp-up), and ACTIVE states.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from backend.ml.domain.enums import ModelStage
from backend.ml.domain.events import (
    MLModelActivated,
    MLModelPromotedToCanary,
    MLModelPromotedToShadow,
)
from backend.ml.domain.exceptions import GovernanceCheckFailedError, ModelNotFoundError
from backend.ml.domain.models import ModelDefinition
from backend.ml.ports.model_storage import ModelRegistryPort
from backend.runtime.events import EventBus

logger = logging.getLogger(__name__)


class ModelReleaseService:
    """Orchestrates progressive deployment gates: SHADOW -> CANARY -> ACTIVE."""

    def __init__(
        self,
        registry: ModelRegistryPort,
        event_bus: EventBus | None = None,
    ) -> None:
        self.registry = registry
        self.event_bus = event_bus or EventBus.get_instance()

    async def promote_to_shadow(
        self,
        organization_id: str,
        model_id: str,
        version_id: str,
    ) -> ModelDefinition:
        """Stage model version in SHADOW mode (receives real inference requests, but cannot mutate)."""
        model = await self.registry.get_model(organization_id, model_id)
        version = await self.registry.get_version(organization_id, version_id)
        if not model or not version:
            raise ModelNotFoundError(f"Model or version not found for [{model_id}:{version_id}]")

        version.stage = ModelStage.SHADOW
        await self.registry.save_version(version)

        model.shadow_version_id = version_id
        model.updated_at = datetime.now(tz=UTC)
        saved = await self.registry.save_model(model)

        await self.event_bus.publish(MLModelPromotedToShadow(organization_id, model_id, version_id))
        logger.info(f"Promoted version [{version_id}] of model [{model_id}] to SHADOW.")
        return saved

    async def promote_to_canary(
        self,
        organization_id: str,
        model_id: str,
        version_id: str,
        traffic_percent: float = 10.0,
    ) -> ModelDefinition:
        """Deploy model version in CANARY mode with bounded traffic split percentage."""
        if not (0.0 <= traffic_percent <= 100.0):
            raise ValueError("Canary traffic percentage must be between 0.0 and 100.0")

        model = await self.registry.get_model(organization_id, model_id)
        version = await self.registry.get_version(organization_id, version_id)
        if not model or not version:
            raise ModelNotFoundError(f"Model or version not found for [{model_id}:{version_id}]")

        version.stage = ModelStage.CANARY
        await self.registry.save_version(version)

        model.canary_version_id = version_id
        model.canary_traffic_percent = traffic_percent
        model.updated_at = datetime.now(tz=UTC)
        saved = await self.registry.save_model(model)

        await self.event_bus.publish(MLModelPromotedToCanary(organization_id, model_id, version_id, traffic_percent))
        logger.info(f"Promoted version [{version_id}] to CANARY at {traffic_percent}% traffic.")
        return saved

    async def activate_model(
        self,
        organization_id: str,
        model_id: str,
        version_id: str,
        approved_by: str,
    ) -> ModelDefinition:
        """Promote model version to primary ACTIVE production stage."""
        model = await self.registry.get_model(organization_id, model_id)
        version = await self.registry.get_version(organization_id, version_id)
        if not model or not version:
            raise ModelNotFoundError(f"Model or version not found for [{model_id}:{version_id}]")

        # Invariant: Must pass fairness evaluation if fairness metrics exist
        if version.fairness_metrics and version.fairness_metrics.get("is_compliant", 1.0) == 0.0:
            raise GovernanceCheckFailedError("Cannot activate model: Failed algorithmic fairness compliance gate.")

        # Update previous active version to rollback target
        if model.active_version_id:
            model.rollback_target_version_id = model.active_version_id

        version.stage = ModelStage.ACTIVE
        version.is_governance_approved = True
        version.approved_by = approved_by
        await self.registry.save_version(version)

        now = datetime.now(tz=UTC)
        model.active_version_id = version_id
        model.stage = ModelStage.ACTIVE
        model.activated_at = now
        model.updated_at = now
        # Reset canary traffic when activated to 100%
        model.canary_version_id = None
        model.canary_traffic_percent = 0.0

        saved = await self.registry.save_model(model)
        await self.event_bus.publish(MLModelActivated(organization_id, model_id, version_id))
        logger.info(f"Model [{model_id}] version [{version_id}] is now fully ACTIVE in production.")
        return saved
