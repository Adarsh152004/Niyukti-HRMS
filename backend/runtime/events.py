"""
Enterprise Runtime — Event Bus contracts.

Defines the Event base model and EventBus interface.
Concrete implementations (Redis Pub/Sub, in-memory) are provided in later nodes.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any


class Event:
    """
    Immutable event emitted by any HRMS component or agent.

    Attributes:
        event_id: Unique identifier for this event instance.
        event_type: Dot-separated event type string, e.g. 'hrms.employee.created'.
        source: Emitting component/agent identifier.
        payload: Arbitrary structured payload (no raw PII).
        correlation_id: Optional ID linking related events (e.g. a command execution).
        occurred_at: UTC timestamp of event creation.
    """

    __slots__ = (
        "correlation_id",
        "event_id",
        "event_type",
        "occurred_at",
        "payload",
        "source",
    )

    def __init__(
        self,
        event_type: str,
        source: str,
        payload: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        self.event_id: str = str(uuid.uuid4())
        self.event_type: str = event_type
        self.source: str = source
        self.payload: dict[str, Any] = payload or {}
        self.correlation_id: str | None = correlation_id
        self.occurred_at: datetime = datetime.now(tz=UTC)

    def __repr__(self) -> str:
        return f"Event(type={self.event_type!r}, source={self.source!r}, id={self.event_id!r})"


# Type alias for async event handler callables
EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus(ABC):
    """
    Abstract event bus interface.

    Supports publish/subscribe semantics for decoupled component communication.
    Concrete implementations must be thread/async safe.
    """

    _instance: EventBus | None = None

    @classmethod
    def get_instance(cls) -> EventBus:
        if cls._instance is None:
            cls._instance = InMemoryEventBus()
        return cls._instance

    @abstractmethod
    async def publish(self, event: Event | Any) -> None:
        """Publish an event to all registered subscribers."""
        ...

    @abstractmethod
    async def subscribe(self, event_type: str, handler: EventHandler) -> str:
        """
        Register an async handler for a given event type.

        Args:
            event_type: The event type pattern to match (exact or wildcard).
            handler: Async callable receiving the Event.

        Returns:
            Subscription ID that can be used to unsubscribe.
        """
        ...

    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> None:
        """Remove a previously registered handler by subscription ID."""
        ...

    @abstractmethod
    async def start(self) -> None:
        """Start the event bus (connect, initialize channels, etc.)."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the event bus gracefully."""
        ...


class InMemoryEventBus(EventBus):
    """
    Simple in-memory event bus for development and testing.

    NOT suitable for production multi-process deployments.
    Replace with Redis Pub/Sub adapter in production.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, dict[str, EventHandler]] = {}

    async def publish(self, event: Event | Any) -> None:
        handlers = self._handlers.get(event.event_type, {})
        wildcard_handlers = self._handlers.get("*", {})
        all_handlers = {**handlers, **wildcard_handlers}
        for handler in all_handlers.values():
            await handler(event)

    async def subscribe(self, event_type: str, handler: EventHandler) -> str:
        sub_id = str(uuid.uuid4())
        self._handlers.setdefault(event_type, {})[sub_id] = handler
        return sub_id

    async def unsubscribe(self, subscription_id: str) -> None:
        for handlers in self._handlers.values():
            handlers.pop(subscription_id, None)

    async def start(self) -> None:
        pass  # No setup needed for in-memory

    async def stop(self) -> None:
        self._handlers.clear()
