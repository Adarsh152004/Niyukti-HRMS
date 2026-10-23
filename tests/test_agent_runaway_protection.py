"""Tests — ExecutionLoop runaway execution protections (max iterations, max plan steps, max tool calls)."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentType
from backend.agents.domain.models import AgentCapability
from backend.agents.orchestration.application.execution_loop import ExecutionLoop
from backend.agents.orchestration.application.task_manager import TaskManager
from backend.agents.orchestration.domain.enums import ExecutionState
from backend.agents.orchestration.domain.models import AgentExecution
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import ReasoningDecision
from backend.agents.reasoning.providers.mock import MockLLMProvider
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_execution_loop_max_iterations_breach_stops_safely():
    provider = MockLLMProvider()
    # Enqueue non-terminating tool decisions
    for i in range(10):
        provider.enqueue_decision(
            ReasoningDecision(
                decision_type=DecisionType.TOOL_CALL,
                selected_tool="employee.get",
                tool_arguments={"employee_id": f"emp-{i}"},
            )
        )

    agent_svc = AgentService()
    task_svc = AgentTaskService()

    cap_read = AgentCapability(capability_id="cap-1", name="Read Emp", resource="employee", actions=["read"])
    agent = await agent_svc.create_agent(
        organization_id="org-acme",
        name="runaway-bot",
        display_name="Runaway Bot",
        agent_type=AgentType.ANALYTICS_AGENT,
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-acme", agent.agent_id)

    task = await task_svc.create_task(organization_id="org-acme", agent_id=agent.agent_id, goal="Runaway goal")

    from backend.agents.application.command_gateway import AgentCommandGateway
    from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
    from backend.agents.tools.application.tool_registry import ToolRegistry
    from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools
    from backend.commands.application.bus import CommandBus
    from backend.commands.application.handlers import GetEmployeeCommandHandler
    from backend.commands.domain.enums import RiskLevel
    from backend.commands.domain.models import CommandMetadata

    bus = CommandBus()
    bus.registry.register(
        "employee.read",
        GetEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.read",
            description="Get employee",
            required_permissions=["EMPLOYEE_READ"],
            risk_level=RiskLevel.LOW,
        ),
    )
    tool_registry = ToolRegistry()
    register_builtin_tools(tool_registry)
    cmd_gateway = AgentCommandGateway(command_bus=bus)
    tool_gateway = ToolExecutionGateway(registry=tool_registry, command_gateway=cmd_gateway)

    reasoning_engine = ReasoningEngine(
        provider=provider,
        tool_gateway=tool_gateway,
        agent_service=agent_svc,
        task_service=task_svc,
        max_steps=1,
    )
    task_mgr = TaskManager(task_service=task_svc)
    loop = ExecutionLoop(
        reasoning_engine=reasoning_engine,
        task_manager=task_mgr,
        max_iterations=3,  # Strict max iterations
    )

    agent_actor = Actor(
        actor_id=agent.actor_id,
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions={"EMPLOYEE_READ"},
    )

    execution = AgentExecution(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        task_id=task.task_id,
    )

    res_exec = await loop.run(execution, agent, task, actor=agent_actor)

    assert res_exec.state == ExecutionState.FAILED
    assert res_exec.failure_reason is not None
    assert "reasoning" in res_exec.failure_reason.lower() or "exceeded" in res_exec.failure_reason.lower()
