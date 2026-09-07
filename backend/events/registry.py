"""
Event Schema Registry — Schema versioning and consumer idempotency state tracking.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EventSchemaDefinition(BaseModel):
    """Registered event type schema contract."""

    event_type: str
    version: int = Field(default=1, ge=1)
    schema_definition: dict[str, Any] = Field(default_factory=dict)
    description: str = Field(default="")
    registered_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class ConsumerOffsetRecord(BaseModel):
    """Tracks consumer processed event IDs to prevent duplicate processing."""

    consumer_group: str
    event_id: str
    processed_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class EventSchemaRegistry:
    """Registry maintaining versioned domain event schemas and consumer offsets."""

    _instance: EventSchemaRegistry | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._schemas: dict[str, dict[int, EventSchemaDefinition]] = {}
        self._processed_offsets: set[str] = set()

    @classmethod
    def get_instance(cls) -> EventSchemaRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def register_schema(
        self,
        event_type: str,
        version: int,
        schema_definition: dict[str, Any] | None = None,
        description: str = "",
    ) -> EventSchemaDefinition:
        """Register a versioned schema definition."""
        defn = EventSchemaDefinition(
            event_type=event_type,
            version=version,
            schema_definition=schema_definition or {},
            description=description,
        )
        async with self._lock:
            if event_type not in self._schemas:
                self._schemas[event_type] = {}
            self._schemas[event_type][version] = defn
            logger.info(f"Registered schema for event '{event_type}' v{version}")
            return defn

    async def get_schema(self, event_type: str, version: int = 1) -> EventSchemaDefinition | None:
        """Retrieve schema definition for event type and version."""
        async with self._lock:
            return self._schemas.get(event_type, {}).get(version)

    async def is_event_processed(self, consumer_group: str, event_id: str) -> bool:
        """Check if an event was already processed by a specific consumer group."""
        key = f"{consumer_group}:{event_id}"
        async with self._lock:
            return key in self._processed_offsets

    async def mark_event_processed(self, consumer_group: str, event_id: str) -> None:
        """Record consumer offset for processed event."""
        key = f"{consumer_group}:{event_id}"
        async with self._lock:
            self._processed_offsets.add(key)

    async def reset(self) -> None:
        """Clear registry for testing."""
        async with self._lock:
            self._schemas.clear()
            self._processed_offsets.clear()
