"""Tests — AI Agent command execution, capability scoping, and non-bypass invariants."""

import pytest

from backend.commands.application.bus import CommandBus, CommandBusExecutionError
from backend.commands.application.handlers import CreateEmployeeCommandHandler, TerminateEmployeeCommandHandler
from backend.commands.domain.enums import CommandStatus, RiskLevel
from backend.commands.domain.models import Command, CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType
from backend.security.application.agent_security_service import AgentAuthenticationError, AgentSecurityService


@pytest.mark.asyncio
async def test_ai_agent_uses_command_bus_with_explicit_capabilities():
    bus = CommandBus()
    handler = CreateEmployeeCommandHandler()
    meta = CommandMetadata(
        command_type="employee.create",
        description="Create employee",
        required_permissions=["EMPLOYEE_CREATE"],
        risk_level=RiskLevel.MEDIUM,
    )
    bus.registry.register("employee.create", handler, meta)

    # Agent actor with explicit capability grant
    agent_actor = Actor(
        actor_id="agent-actor-screening",
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions={"EMPLOYEE_CREATE"},
        metadata={"capabilities": ["employee.create"]},
    )

    cmd = Command(
        command_type="employee.create",
        actor_id=agent_actor.actor_id,
        organization_id=agent_actor.organization_id,
        payload={"first_name": "ScreenedCandidate"},
    )

    ctx = bus.build_context(agent_actor)
    res = await bus.dispatch(cmd, ctx)

    assert res.status == CommandStatus.SUCCEEDED
    assert res.result_data["first_name"] == "ScreenedCandidate"


@pytest.mark.asyncio
async def test_ai_agent_unauthorized_command_denied():
    bus = CommandBus()
    handler = TerminateEmployeeCommandHandler()
    meta = CommandMetadata(
        command_type="employee.terminate",
        description="Terminate employee",
        required_permissions=["EMPLOYEE_DELETE"],
        risk_level=RiskLevel.HIGH,
    )
    bus.registry.register("employee.terminate", handler, meta)

    # Agent without EMPLOYEE_DELETE permission
    agent_actor = Actor(
        actor_id="agent-actor-screening",
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions=set(),
    )

    cmd = Command(
        command_type="employee.terminate",
        actor_id=agent_actor.actor_id,
        organization_id=agent_actor.organization_id,
    )

    ctx = bus.build_context(agent_actor)
    with pytest.raises(CommandBusExecutionError, match="unauthorized"):
        await bus.dispatch(cmd, ctx)


def test_suspended_agent_authentication_blocked():
    agent_svc = AgentSecurityService()
    agent = agent_svc.register_agent(
        name="Scout Agent",
        organization_id="org-acme",
        capabilities=["employee.read"],
    )

    agent_svc.suspend_agent(agent.agent_id)

    with pytest.raises(AgentAuthenticationError):
        agent_svc.authenticate_agent(agent.agent_id, "org-acme")
