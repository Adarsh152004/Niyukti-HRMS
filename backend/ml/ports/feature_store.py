"""
Feature Store Port — Contract for offline batch and online low-latency feature retrieval.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from backend.ml.domain.models import FeatureDefinition


class FeatureStorePort(ABC):
    """Abstraction for feature definition persistence and online feature vector serving."""

    @abstractmethod
    async def register_feature(self, feature: FeatureDefinition) -> FeatureDefinition:
        """Persist or update a feature definition."""
        ...

    @abstractmethod
    async def get_feature(self, feature_name: str) -> FeatureDefinition | None:
        """Fetch feature definition by name."""
        ...

    @abstractmethod
    async def list_features(self) -> Sequence[FeatureDefinition]:
        """List all registered feature definitions."""
        ...

    @abstractmethod
    async def save_online_features(
        self,
        organization_id: str,
        entity_id: str,
        features: dict[str, Any],
    ) -> None:
        """Store online feature vector for an entity (e.g. employee_id)."""
        ...

    @abstractmethod
    async def get_online_features(
        self,
        organization_id: str,
        entity_id: str,
        feature_names: Sequence[str],
    ) -> dict[str, Any]:
        """Fetch online feature vector with low latency."""
        ...
