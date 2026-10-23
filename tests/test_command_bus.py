"""Tests — CommandBus orchestration, validation, registration, and lifecycle state transitions."""

import pytest

from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import CreateEmployeeCommandHandler
from backend.commands.application.registry import CommandAlreadyRegisteredError, CommandRegistry
from backend.commands.domain.enums import CommandStatus, RiskLevel
from backend.commands.domain.models import Command, CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType


def test_command_creation_and_payload_hash():
    cmd = Command(
        command_type="employee.create",
        actor_id="actor-001",
        organization_id="org-acme",
        payload={"first_name": "John", "last_name": "Doe"},
    )
    assert cmd.command_id.startswith("cmd-")
    assert cmd.status == CommandStatus.RECEIVED
    assert len(cmd.payload_hash) == 64  # SHA-256 length


def test_command_valid_state_transitions():
    cmd = Command(
        command_type="employee.create",
        actor_id="actor-001",
        organization_id="org-acme",
    )
    cmd.transition_to(CommandStatus.VALIDATING)
    assert cmd.status == CommandStatus.VALIDATING

    cmd.transition_to(CommandStatus.AUTHORIZED)
    assert cmd.status == CommandStatus.AUTHORIZED

    cmd.transition_to(CommandStatus.POLICY_CHECKED)
    assert cmd.status == CommandStatus.POLICY_CHECKED

    cmd.transition_to(CommandStatus.EXECUTING)
    assert cmd.status == CommandStatus.EXECUTING

    cmd.transition_to(CommandStatus.SUCCEEDED)
    assert cmd.status == CommandStatus.SUCCEEDED


def test_command_invalid_state_transition_fails():
    cmd = Command(
        command_type="employee.create",
        actor_id="actor-001",
        organization_id="org-acme",
    )
    # Direct transition from RECEIVED to SUCCEEDED must fail
    with pytest.raises(ValueError, match="Invalid command status transition"):
        cmd.transition_to(CommandStatus.SUCCEEDED)


def test_command_registry_duplicate_registration_prevented():
    registry = CommandRegistry()
    handler = CreateEmployeeCommandHandler()
    meta = CommandMetadata(
        command_type="employee.create",
        description="Create employee",
    )

    registry.register("employee.create", handler, meta)

    # Registering duplicate command type must raise CommandAlreadyRegisteredError
    with pytest.raises(CommandAlreadyRegisteredError):
        registry.register("employee.create", handler, meta)


@pytest.mark.asyncio
async def test_command_bus_successful_dispatch():
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
    cmd = Command(
        command_type="employee.create",
        actor_id=actor.actor_id,
        organization_id=actor.organization_id,
        payload={"first_name": "Alice", "last_name": "Smith"},
    )

    ctx = bus.build_context(actor)
    res = await bus.dispatch(cmd, ctx)

    assert res.status == CommandStatus.SUCCEEDED
    assert res.result_data["first_name"] == "Alice"
    assert res.result_data["organization_id"] == "org-acme"
