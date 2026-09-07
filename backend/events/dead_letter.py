"""
Dead-Letter Queue (DLQ) & Event Replay Engine.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class DeadLetterEvent(BaseModel):
    """Encapsulates a failed event with failure context for diagnostic inspection and replay."""

    dlq_id: str = Field(default_factory=lambda: f"dlq-{uuid.uuid4()}")
    original_event: dict[str, Any]
    consumer_name: str
    error_message: str
    stack_trace: str | None = None
    retry_count: int = Field(default=0)
    failed_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    replayed: bool = Field(default=False)
    replayed_at: datetime | None = None


class DeadLetterQueueService:
    """Service managing captured dead-letter events and replay workflows."""

    _instance: DeadLetterQueueService | None = None

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._lock = asyncio.Lock()
        self._dlq_records: dict[str, DeadLetterEvent] = {}
        self.event_bus = event_bus or EventBus.get_instance()

    @classmethod
    def get_instance(cls) -> DeadLetterQueueService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def record_dead_letter(
        self,
        event: Event,
        consumer_name: str,
        error_message: str,
        stack_trace: str | None = None,
        retry_count: int = 0,
    ) -> DeadLetterEvent:
        """Capture failed event in DLQ."""
        event_dict = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "source": event.source,
            "payload": event.payload,
            "correlation_id": event.correlation_id,
            "causation_id": getattr(event, "causation_id", None),
            "timestamp": event.occurred_at.isoformat() if hasattr(event, "occurred_at") and event.occurred_at else None,
        }

        record = DeadLetterEvent(
            original_event=event_dict,
            consumer_name=consumer_name,
            error_message=error_message,
            stack_trace=stack_trace,
            retry_count=retry_count,
        )

        async with self._lock:
            self._dlq_records[record.dlq_id] = record
            logger.error(f"Event '{event.event_type}' moved to DLQ [{record.dlq_id}]: {error_message}")
            return record

    async def list_dead_letters(
        self, consumer_name: str | None = None, unresolved_only: bool = True
    ) -> Sequence[DeadLetterEvent]:
        """List dead letter events with optional filters."""
        async with self._lock:
            results = list(self._dlq_records.values())
            if consumer_name:
                results = [r for r in results if r.consumer_name == consumer_name]
            if unresolved_only:
                results = [r for r in results if not r.replayed]
            return results

    async def replay_event(self, dlq_id: str) -> bool:
        """Replay dead-letter event back to EventBus."""
        async with self._lock:
            record = self._dlq_records.get(dlq_id)
            if not record:
                raise ValueError(f"DLQ record '{dlq_id}' not found.")

            orig = record.original_event
            event = Event(
                event_type=orig["event_type"],
                source=orig.get("source", "dlq_replay"),
                payload=orig.get("payload", {}),
                correlation_id=orig.get("correlation_id"),
            )

            record.replayed = True
            record.replayed_at = datetime.now(tz=UTC)

        await self.event_bus.publish(event)
        logger.info(f"Replayed DLQ event [{dlq_id}] to EventBus as '{event.event_type}'")
        return True
