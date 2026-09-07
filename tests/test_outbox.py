"""Tests — Outbox model and event payload formatting."""

from datetime import UTC, datetime

from backend.hrms.domain.events import EmployeeCreated
from backend.hrms.infrastructure.database.models.outbox import OutboxEventModel


def test_outbox_model_instantiation():
    now = datetime.now(tz=UTC)
    outbox = OutboxEventModel(
        id="outbox-001",
        organization_id="org-acme",
        event_id="evt-001",
        event_type="EmployeeCreated",
        aggregate_id="emp-001",
        payload={"first_name": "John", "last_name": "Doe"},
        occurred_at=now,
        status="PENDING",
    )
    assert outbox.id == "outbox-001"
    assert outbox.event_type == "EmployeeCreated"
    assert outbox.status == "PENDING"
    assert outbox.payload["first_name"] == "John"


def test_domain_event_to_outbox_payload():
    event = EmployeeCreated(
        organization_id="org-acme",
        aggregate_id="emp-001",
        actor={"actor_id": "usr-1", "actor_type": "HUMAN"},
        metadata={"employee_code": "EMP-001"},
    )
    payload = event.model_dump()
    assert payload["organization_id"] == "org-acme"
    assert payload["aggregate_id"] == "emp-001"
    assert payload["event_type"] == "EmployeeCreated"
    assert payload["metadata"]["employee_code"] == "EMP-001"
