"""Tests — Agent Security Invariants, Tenant Isolation, and Non-Bypass Protection."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.application.command_gateway import AgentCommandGateway
from backend.agents.application.execution_context import AgentExecutionContextFactory
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.exceptions import AgentCapabilityError, AgentSecurityError
from backend.agents.domain.models import Agent, AgentCapability, AgentTask
from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import CreateEmployeeCommandHandler
from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import CommandMetadata


@pytest.mark.asyncio
async def test_duplicate_agent_registration_fails():
    service = AgentService()
    await service.create_agent(organization_id="org-acme", name="agent-uniq", display_name="Unique Agent")

    with pytest.raises(AgentSecurityError, match="already exists"):
        await service.create_agent(organization_id="org-acme", name="agent-uniq", display_name="Duplicate Agent")


@pytest.mark.asyncio
async def test_inactive_agent_command_execution_blocked():
    bus = CommandBus()
    gateway = AgentCommandGateway(command_bus=bus)

    cap_create = AgentCapability(
        capability_id="cap-1",
        name="Create Emp",
        resource="employee",
        actions=["create"],
    )

    agent = Agent(
        organization_id="org-acme",
        name="paused-agent",
        display_name="Paused Agent",
        actor_id="actor-paused",
        status=AgentStatus.PAUSED,  # Inactive status
        capabilities=[cap_create],
    )

    task = AgentTask(organization_id="org-acme", agent_id=agent.agent_id, goal="Create emp")
    ctx = AgentExecutionContextFactory.create_context(agent, task)

    with pytest.raises(AgentSecurityError, match="cannot execute action in status"):
        await gateway.request_action(
            agent=agent,
            context=ctx,
            resource="employee",
            action="create",
            command_type="employee.create",
            payload={"first_name": "Test"},
        )


@pytest.mark.asyncio
async def test_agent_capability_mismatch_rejected():
    bus = CommandBus()
    gateway = AgentCommandGateway(command_bus=bus)

    cap_read = AgentCapability(
        capability_id="cap-1",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )

    agent = Agent(
        organization_id="org-acme",
        name="reader-agent",
        display_name="Reader Agent",
        actor_id="actor-reader",
        status=AgentStatus.ACTIVE,
        capabilities=[cap_read],
    )

    task = AgentTask(organization_id="org-acme", agent_id=agent.agent_id, goal="Delete emp")
    ctx = AgentExecutionContextFactory.create_context(agent, task)

    # Attempting 'terminate' action when agent only has 'read' capability
    with pytest.raises(AgentCapabilityError, match="lacks required capability"):
        await gateway.request_action(
            agent=agent,
            context=ctx,
            resource="employee",
            action="terminate",
            command_type="employee.terminate",
            payload={"employee_id": "emp-1"},
        )


@pytest.mark.asyncio
async def test_cross_tenant_agent_gateway_access_denied():
    bus = CommandBus()
    bus.registry.register(
        "employee.create",
        CreateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.create",
            description="Create employee",
            required_permissions=["EMPLOYEE_CREATE"],
            risk_level=RiskLevel.MEDIUM,
        ),
    )
    gateway = AgentCommandGateway(command_bus=bus)

    cap_create = AgentCapability(
        capability_id="cap-create",
        name="Create Emp",
        resource="employee",
        actions=["create"],
    )

    agent = Agent(
        organization_id="org-tenant-a",
        name="agent-a",
        display_name="Agent A",
        actor_id="actor-a",
        status=AgentStatus.ACTIVE,
        capabilities=[cap_create],
    )

    task = AgentTask(organization_id="org-tenant-b", agent_id=agent.agent_id, goal="Hack tenant b")
    ctx = AgentExecutionContextFactory.create_context(agent, task)

    with pytest.raises(AgentSecurityError, match="Cross-tenant access attempt"):
        await gateway.request_action(
            agent=agent,
            context=ctx,
            resource="employee",
            action="create",
            command_type="employee.create",
            payload={"first_name": "Hack"},
        )
