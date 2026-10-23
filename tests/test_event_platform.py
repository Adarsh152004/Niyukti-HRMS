"""
Tests for Event Platform (Schema Registry, Offset Tracking, DLQ, and Replay).
"""

from __future__ import annotations

import pytest

from backend.events.dead_letter import DeadLetterQueueService
from backend.events.registry import EventSchemaRegistry
from backend.runtime.events import Event, EventBus


@pytest.mark.asyncio
async def test_event_schema_registry():
    registry = EventSchemaRegistry.get_instance()
    await registry.reset()

    # Register schema v1
    defn = await registry.register_schema(
        event_type="employee.onboarded",
        version=1,
        schema_definition={"type": "object", "properties": {"employee_id": {"type": "string"}}},
        description="Emitted when employee onboarding completes",
    )
    assert defn.version == 1

    fetched = await registry.get_schema("employee.onboarded", version=1)
    assert fetched is not None
    assert fetched.description == "Emitted when employee onboarding completes"

    # Consumer offset idempotency tracking
    consumer_group = "notification_service"
    event_id = "evt-12345"

    assert await registry.is_event_processed(consumer_group, event_id) is False
    await registry.mark_event_processed(consumer_group, event_id)
    assert await registry.is_event_processed(consumer_group, event_id) is True


@pytest.mark.asyncio
async def test_dead_letter_queue_and_replay():
    event_bus = EventBus.get_instance()
    dlq_service = DeadLetterQueueService(event_bus=event_bus)

    failed_event = Event(
        event_type="payroll.disbursement.failed",
        source="payroll_processor",
        payload={"payroll_run_id": "pr-101", "amount": 50000.0},
    )

    # Capture in DLQ
    dlq_record = await dlq_service.record_dead_letter(
        event=failed_event,
        consumer_name="bank_gateway_consumer",
        error_message="Connection refused to banking API",
        retry_count=3,
    )
    assert dlq_record.dlq_id.startswith("dlq-")
    assert dlq_record.replayed is False

    # List unresolved DLQ records
    unresolved = await dlq_service.list_dead_letters(unresolved_only=True)
    assert any(r.dlq_id == dlq_record.dlq_id for r in unresolved)

    # Replay event
    replayed = await dlq_service.replay_event(dlq_record.dlq_id)
    assert replayed is True

    # Check that it is now marked replayed
    unresolved_after = await dlq_service.list_dead_letters(unresolved_only=True)
    assert not any(r.dlq_id == dlq_record.dlq_id for r in unresolved_after)
