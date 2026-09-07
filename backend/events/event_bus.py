"""
AI-Powered Intelligent HRMS — Event Bus Adapter.
"""

from __future__ import annotations

from typing import Any

from backend.runtime.events import Event, EventBus


def get_event_bus() -> EventBus:
    """Return the global EventBus instance."""
    return EventBus.get_instance()
