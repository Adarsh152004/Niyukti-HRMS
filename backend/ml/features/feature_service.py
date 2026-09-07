"""
Feature Service — Master façade for feature registration, online serving, and validation.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from backend.ml.domain.models import FeatureDefinition
from backend.ml.features.definitions import STANDARD_HR_FEATURES
from backend.ml.features.feature_validation import FeatureValidationResult, FeatureValidator
from backend.ml.infrastructure.in_memory import InMemoryFeatureStore
from backend.ml.ports.feature_store import FeatureStorePort

logger = logging.getLogger(__name__)


class FeatureService:
    """Service managing feature definitions, online feature store ingestion, and validation."""

    _instance: FeatureService | None = None

    def __init__(self, feature_store: FeatureStorePort | None = None) -> None:
        self.store = feature_store or InMemoryFeatureStore.get_instance()

    @classmethod
    def get_instance(cls) -> FeatureService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize_standard_features(self) -> None:
        """Register default HR feature definitions."""
        for feat in STANDARD_HR_FEATURES:
            await self.store.register_feature(feat)

    async def register_feature_definition(self, definition: FeatureDefinition) -> FeatureDefinition:
        """Register a custom feature definition."""
        return await self.store.register_feature(definition)

    async def get_feature_definition(self, feature_name: str) -> FeatureDefinition | None:
        return await self.store.get_feature(feature_name)

    async def list_feature_definitions(self) -> Sequence[FeatureDefinition]:
        return await self.store.list_features()

    async def store_entity_features(
        self,
        organization_id: str,
        entity_id: str,
        features: dict[str, Any],
    ) -> None:
        """Ingest online feature vector for an entity."""
        await self.store.save_online_features(organization_id, entity_id, features)

    async def get_entity_features(
        self,
        organization_id: str,
        entity_id: str,
        feature_names: Sequence[str],
    ) -> dict[str, Any]:
        """Retrieve online feature vector."""
        return await self.store.get_online_features(organization_id, entity_id, feature_names)

    async def validate_features_for_model(
        self,
        features: dict[str, Any],
        required_feature_names: Sequence[str],
    ) -> FeatureValidationResult:
        """Fetch definitions for required features and validate incoming vector."""
        definitions: list[FeatureDefinition] = []
        for f_name in required_feature_names:
            f_def = await self.store.get_feature(f_name)
            if not f_def:
                # Create ad-hoc definition if not explicitly registered
                f_def = FeatureDefinition(name=f_name, source_table="unknown", transformation_logic="raw", owner="system")
            definitions.append(f_def)

        return FeatureValidator.validate_vector(features, definitions)
