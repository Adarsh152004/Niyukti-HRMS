"""Tests — Capability-aware Tool Discovery and Hidden Tool Execution Blocking."""

import pytest

from backend.agents.application.execution_context import AgentExecutionContextFactory
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.models import Agent, AgentCapability, AgentTask
from backend.agents.tools.application.tool_discovery import ToolDiscovery
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.domain.exceptions import ToolAccessDeniedError
from backend.agents.tools.domain.models import ToolProposal
from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools


def test_capability_aware_tool_discovery():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    discovery = ToolDiscovery(registry=registry)

    # Agent with ONLY 'employee:read' capability
    cap_emp = AgentCapability(
        capability_id="cap-1",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )

    agent = Agent(
        organization_id="org-acme",
        name="emp-reader",
        display_name="Emp Reader",
        actor_id="actor-reader",
        capabilities=[cap_emp],
    )

    task = AgentTask(organization_id="org-acme", agent_id=agent.agent_id, goal="Discover tools")
    ctx = AgentExecutionContextFactory.create_context(agent, task)

    tools = discovery.discover_tools(agent, ctx)
    tool_ids = [t.tool_id for t in tools]

    assert "employee.get" in tool_ids
    assert "employee.list" in tool_ids
    # Department & Skill tools are hidden because agent lacks department:read / skill:read
    assert "department.get" not in tool_ids
    assert "skill.get" not in tool_ids


@pytest.mark.asyncio
async def test_hidden_tool_execution_blocked():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    tool_gateway = ToolExecutionGateway(registry=registry, command_gateway=None)

    # Agent without department:read capability
    agent = Agent(
        organization_id="org-acme",
        name="no-dept-agent",
        display_name="No Dept Agent",
        actor_id="actor-no-dept",
        status=AgentStatus.ACTIVE,
        capabilities=[],
    )

    task = AgentTask(organization_id="org-acme", agent_id=agent.agent_id, goal="Try hidden tool")
    ctx = AgentExecutionContextFactory.create_context(agent, task)

    proposal = ToolProposal(tool_id="department.get", arguments={"department_id": "dept-1"})

    with pytest.raises(ToolAccessDeniedError, match="lacks capability for tool"):
        await tool_gateway.execute_proposal(agent=agent, context=ctx, proposal=proposal)
