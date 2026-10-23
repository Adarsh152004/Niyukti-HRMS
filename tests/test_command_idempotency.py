"""Tests — Idempotency key deduplication and payload hash mismatch prevention."""

import pytest

from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import CreateEmployeeCommandHandler
from backend.commands.application.idempotency import IdempotencyMismatchError
from backend.commands.domain.enums import CommandStatus, RiskLevel
from backend.commands.domain.models import Command, CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_idempotent_command_execution():
    bus = CommandBus()
    handler = CreateEmployeeCommandHandler()
    meta = CommandMetadata(
        command_type="employee.create",
        description="Create employee",
        required_permissions=["EMPLOYEE_CREATE"],
        risk_level=RiskLevel.MEDIUM,
    )
    bus.registry.register("employee.create", handler, meta)

    actor = Actor(
        actor_id="usr-actor-001",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"EMPLOYEE_CREATE"},
    )
    ctx = bus.build_context(actor)

    cmd1 = Command(
        command_type="employee.create",
        actor_id=actor.actor_id,
        organization_id=actor.organization_id,
        payload={"first_name": "Alice", "last_name": "Smith"},
        idempotency_key="idemp-key-100",
    )

    res1 = await bus.dispatch(cmd1, ctx)
    assert res1.status == CommandStatus.SUCCEEDED

    # Submit second identical command with same idempotency key
    cmd2 = Command(
        command_type="employee.create",
        actor_id=actor.actor_id,
        organization_id=actor.organization_id,
        payload={"first_name": "Alice", "last_name": "Smith"},
        idempotency_key="idemp-key-100",
    )

    res2 = await bus.dispatch(cmd2, ctx)
    assert res2.status == CommandStatus.SUCCEEDED
    assert res2.result_data == res1.result_data


@pytest.mark.asyncio
async def test_idempotency_key_reuse_with_different_payload_fails():
    bus = CommandBus()
    handler = CreateEmployeeCommandHandler()
    meta = CommandMetadata(
        command_type="employee.create",
        description="Create employee",
        required_permissions=["EMPLOYEE_CREATE"],
    )
    bus.registry.register("employee.create", handler, meta)

    actor = Actor(
        actor_id="usr-actor-001",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"EMPLOYEE_CREATE"},
    )
    ctx = bus.build_context(actor)

    cmd1 = Command(
        command_type="employee.create",
        actor_id=actor.actor_id,
        organization_id=actor.organization_id,
        payload={"first_name": "Alice"},
        idempotency_key="idemp-key-200",
    )
    await bus.dispatch(cmd1, ctx)

    # Submitting same idempotency key with DIFFERENT payload must fail!
    cmd2 = Command(
        command_type="employee.create",
        actor_id=actor.actor_id,
        organization_id=actor.organization_id,
        payload={"first_name": "BOB_DIFFERENT"},
        idempotency_key="idemp-key-200",
    )

    with pytest.raises(IdempotencyMismatchError):
        await bus.dispatch(cmd2, ctx)
