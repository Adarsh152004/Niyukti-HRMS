"""Tests — Verification that LLM cannot grant capabilities, modify permissions, bypass CommandBus, or execute direct code."""

import pytest

from backend.agents.application.command_gateway import AgentCommandGateway
from backend.agents.domain.models import Agent, AgentTask
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.domain.exceptions import ToolValidationError
from backend.agents.tools.domain.models import ToolDefinition, ToolProposal
from backend.commands.application.bus import CommandBus


def test_llm_cannot_register_prohibited_execution_tools():
    registry = ToolRegistry()

    malicious_tool = ToolDefinition(
        tool_id="raw_database_query",
        name="Raw Query",
        description="Execute arbitrary SQL",
        resource="database",
        action="execute",
        command_type="raw_database_query",
    )

    with pytest.raises(ToolValidationError, match="Prohibited tool ID"):
        registry.register_tool(malicious_tool)


@pytest.mark.asyncio
async def test_llm_cannot_grant_self_capabilities_or_bypass_command_bus():
    bus = CommandBus()
    cmd_gateway = AgentCommandGateway(command_bus=bus)
    tool_gateway = ToolExecutionGateway(command_gateway=cmd_gateway)

    agent = Agent(
        organization_id="org-acme",
        name="unauthorized-bot",
        display_name="Unauthorized Bot",
        actor_id="actor-unauth",
        capabilities=[],  # Zero capabilities declared
    )
    task = AgentTask(organization_id="org-acme", agent_id=agent.agent_id, goal="Elevate privileges")

    from backend.agents.application.execution_context import AgentExecutionContextFactory

    ctx = AgentExecutionContextFactory.create_context(agent, task)

    from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools

    register_builtin_tools(tool_gateway.registry)

    # Attempt to run employee.get tool without capability
    proposal = ToolProposal(
        tool_id="employee.get",
        arguments={"employee_id": "emp-101"},
    )

    from backend.agents.tools.domain.exceptions import ToolAccessDeniedError

    with pytest.raises(ToolAccessDeniedError):
        await tool_gateway.execute_proposal(agent, ctx, proposal)
