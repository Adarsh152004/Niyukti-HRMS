"""
AI-Powered Intelligent HRMS — Outbox Domain Models & Repository Interface.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from backend.runtime.events import Event


@dataclass
class OutboxEvent:
    """Represents an outbox event staged for reliable broadcast."""

    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    tenant_id: str = "tenant-default"
    payload: dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    status: str = "PENDING"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: datetime | None = None
    last_error: str | None = None

    def to_domain_event(self) -> Event:
        return Event(
            event_type=self.event_type,
            source=f"{self.aggregate_type}:{self.aggregate_id}",
            payload={**self.payload, "tenant_id": self.tenant_id},
        )


class OutboxRepository:
    """In-memory threadsafe repository for staging and draining outbox events."""

    def __init__(self) -> None:
        self._events: dict[str, OutboxEvent] = {}

    async def save(self, event: OutboxEvent) -> None:
        self._events[event.event_id] = event

    async def fetch_pending(self, limit: int = 50) -> list[OutboxEvent]:
        pending = [e for e in self._events.values() if e.status == "PENDING"]
        return pending[:limit]

    async def mark_published(self, event_id: str) -> None:
        if event_id in self._events:
            self._events[event_id].status = "PUBLISHED"
            self._events[event_id].published_at = datetime.now(timezone.utc)

    async def mark_failed(self, event_id: str, error: str) -> None:
        if event_id in self._events:
            self._events[event_id].status = "FAILED"
            self._events[event_id].last_error = error

    async def increment_retry(self, event_id: str) -> None:
        if event_id in self._events:
            self._events[event_id].retry_count += 1


_outbox_repo_instance = OutboxRepository()


def get_outbox_repository() -> OutboxRepository:
    return _outbox_repo_instance
