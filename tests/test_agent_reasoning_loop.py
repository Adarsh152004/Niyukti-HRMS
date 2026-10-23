"""Tests — Bounded Reasoning Engine loop, max steps enforcement, and infinite loop detection."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.application.command_gateway import AgentCommandGateway
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentType, TaskStatus
from backend.agents.domain.models import AgentCapability
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import ReasoningDecision
from backend.agents.reasoning.providers.mock import MockLLMProvider
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import GetEmployeeCommandHandler
from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_reasoning_engine_direct_answer_completion():
    provider = MockLLMProvider()
    provider.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.ANSWER,
            explanation="Calculated answer directly.",
            final_response="The result is 42.",
        )
    )

    agent_service = AgentService()
    task_service = AgentTaskService()

    cap_read = AgentCapability(
        capability_id="cap-1",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )

    agent = await agent_service.create_agent(
        organization_id="org-acme",
        name="math-bot",
        display_name="Math Bot",
        agent_type=AgentType.ANALYTICS_AGENT,
        capabilities=[cap_read],
    )
    await agent_service.activate_agent("org-acme", agent.agent_id)

    task = await task_service.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Calculate 6 * 7",
    )

    engine = ReasoningEngine(
        provider=provider,
        agent_service=agent_service,
        task_service=task_service,
        max_steps=5,
    )

    run = await engine.run_task_reasoning(agent=agent, task=task)

    assert run.status == "COMPLETED"
    assert run.step_count == 1

    updated_task = await task_service.get_task("org-acme", task.task_id)
    assert updated_task.status == TaskStatus.COMPLETED
    assert updated_task.output["final_response"] == "The result is 42."


@pytest.mark.asyncio
async def test_reasoning_engine_max_steps_exceeded_fails_safely():
    provider = MockLLMProvider()
    # Enqueue decisions that call non-repeated tool calls until max_steps
    for i in range(5):
        provider.enqueue_decision(
            ReasoningDecision(
                decision_type=DecisionType.TOOL_CALL,
                selected_tool="employee.get",
                tool_arguments={"employee_id": f"emp-{i}"},
            )
        )

    agent_service = AgentService()
    task_service = AgentTaskService()

    cap_read = AgentCapability(
        capability_id="cap-1",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )

    agent = await agent_service.create_agent(
        organization_id="org-acme",
        name="looping-bot",
        display_name="Looping Bot",
        agent_type=AgentType.ANALYTICS_AGENT,
        capabilities=[cap_read],
    )
    await agent_service.activate_agent("org-acme", agent.agent_id)

    task = await task_service.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Endless loop task",
    )

    bus = CommandBus()
    bus.registry.register(
        "employee.read",
        GetEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.read",
            description="Get employee details",
            required_permissions=["EMPLOYEE_READ"],
            risk_level=RiskLevel.LOW,
        ),
    )
    cmd_gateway = AgentCommandGateway(command_bus=bus)
    tool_gateway = ToolExecutionGateway(command_gateway=cmd_gateway)

    engine = ReasoningEngine(
        provider=provider,
        tool_gateway=tool_gateway,
        agent_service=agent_service,
        task_service=task_service,
        max_steps=3,  # Set strict step limit
    )

    agent_actor = Actor(
        actor_id=agent.actor_id,
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions={"EMPLOYEE_READ"},
    )

    run = await engine.run_task_reasoning(agent=agent, task=task, actor=agent_actor)

    assert run.status == "FAILED"

    updated_task = await task_service.get_task("org-acme", task.task_id)
    assert updated_task.status == TaskStatus.FAILED
    assert "Exceeded maximum reasoning steps" in updated_task.failure_reason


@pytest.mark.asyncio
async def test_reasoning_engine_repeated_tool_call_loop_detected():
    provider = MockLLMProvider()
    # Enqueue identical tool call twice
    for _ in range(2):
        provider.enqueue_decision(
            ReasoningDecision(
                decision_type=DecisionType.TOOL_CALL,
                selected_tool="employee.get",
                tool_arguments={"employee_id": "emp-same"},
            )
        )

    agent_service = AgentService()
    task_service = AgentTaskService()

    cap_read = AgentCapability(
        capability_id="cap-1",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )

    agent = await agent_service.create_agent(
        organization_id="org-acme",
        name="stuck-bot",
        display_name="Stuck Bot",
        agent_type=AgentType.ANALYTICS_AGENT,
        capabilities=[cap_read],
    )
    await agent_service.activate_agent("org-acme", agent.agent_id)

    task = await task_service.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Repeated call task",
    )

    bus = CommandBus()
    bus.registry.register(
        "employee.read",
        GetEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.read",
            description="Get employee details",
            required_permissions=["EMPLOYEE_READ"],
            risk_level=RiskLevel.LOW,
        ),
    )
    cmd_gateway = AgentCommandGateway(command_bus=bus)
    tool_gateway = ToolExecutionGateway(command_gateway=cmd_gateway)

    engine = ReasoningEngine(
        provider=provider,
        tool_gateway=tool_gateway,
        agent_service=agent_service,
        task_service=task_service,
        max_steps=10,
    )

    agent_actor = Actor(
        actor_id=agent.actor_id,
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions={"EMPLOYEE_READ"},
    )

    run = await engine.run_task_reasoning(agent=agent, task=task, actor=agent_actor)

    assert run.status == "FAILED"

    updated_task = await task_service.get_task("org-acme", task.task_id)
    assert updated_task.status == TaskStatus.FAILED
    assert "Repeated tool call loop detected" in updated_task.failure_reason
