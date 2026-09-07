"""Tests — Unit of Work contract and outbox staging."""

import pytest

from backend.hrms.domain.events import EmployeeCreated
from backend.hrms.infrastructure.database.unit_of_work import UnitOfWork


def test_unit_of_work_repositories_present():
    uow = UnitOfWork()
    assert uow.organizations is not None
    assert uow.departments is not None
    assert uow.designations is not None
    assert uow.roles is not None
    assert uow.employees is not None
    assert uow.skills is not None
    assert uow.employee_skills is not None
    assert uow.documents is not None


@pytest.mark.asyncio
async def test_unit_of_work_stage_outbox_event():
    uow = UnitOfWork()
    event = EmployeeCreated(
        organization_id="org-acme",
        aggregate_id="emp-001",
        actor={"actor_id": "usr-1", "actor_type": "HUMAN"},
        metadata={"employee_code": "EMP-001"},
    )
    outbox_entry = await uow.stage_outbox_event(event)
    assert outbox_entry.organization_id == "org-acme"
    assert outbox_entry.event_type == "EmployeeCreated"
    assert outbox_entry.aggregate_id == "emp-001"
    assert outbox_entry.status == "PENDING"
