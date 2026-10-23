"""Tests — End-to-end Agent Intelligence Integration flow with CommandBus and HITL gate."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.application.command_gateway import AgentCommandGateway
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentType, TaskStatus
from backend.agents.domain.models import AgentCapability
from backend.agents.memory.application.memory_service import MemoryService
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import ReasoningDecision
from backend.agents.reasoning.providers.mock import MockLLMProvider
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools
from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import (
    CreateEmployeeCommandHandler,
    GetEmployeeCommandHandler,
    TerminateEmployeeCommandHandler,
)
from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_end_to_end_agent_intelligence_flow_with_tool_call_and_hitl():
    # 1. Setup CommandBus, Registry, Gateway
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
    bus.registry.register(
        "employee.terminate",
        TerminateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.terminate",
            description="Terminate employee",
            required_permissions=["EMPLOYEE_DELETE"],
            risk_level=RiskLevel.HIGH,
            requires_approval=True,
        ),
    )

    tool_registry = ToolRegistry()
    register_builtin_tools(tool_registry)

    cmd_gateway = AgentCommandGateway(command_bus=bus)
    tool_gateway = ToolExecutionGateway(registry=tool_registry, command_gateway=cmd_gateway)

    # 2. Setup AI Agent and Services
    agent_service = AgentService()
    task_service = AgentTaskService()
    mem_service = MemoryService()

    cap_read = AgentCapability(
        capability_id="cap-read",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )
    cap_create = AgentCapability(
        capability_id="cap-create",
        name="Create Emp",
        resource="employee",
        actions=["create"],
    )
    cap_term = AgentCapability(
        capability_id="cap-term",
        name="Terminate Emp",
        resource="employee",
        actions=["terminate"],
        requires_hitl=True,
    )

    agent = await agent_service.create_agent(
        organization_id="org-acme",
        name="intelligent-hr-bot",
        display_name="Intelligent HR Bot",
        agent_type=AgentType.HR_AGENT,
        capabilities=[cap_read, cap_create, cap_term],
    )
    await agent_service.activate_agent("org-acme", agent.agent_id)

    # Agent Security Actor with Node 4 permissions
    agent_actor = Actor(
        actor_id=agent.actor_id,
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions={"EMPLOYEE_READ", "EMPLOYEE_CREATE", "EMPLOYEE_DELETE"},
    )

    # 3. Test Flow 1: Tool execution for employee.create -> ANSWER
    provider = MockLLMProvider()
    provider.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.TOOL_CALL,
            selected_tool="employee.get",
            tool_arguments={"employee_id": "emp-100"},
        )
    )
    provider.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.ANSWER,
            explanation="Processed employee query.",
            final_response="Employee #100 processed successfully.",
        )
    )

    task1 = await task_service.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Query employee #100",
    )

    engine = ReasoningEngine(
        provider=provider,
        tool_gateway=tool_gateway,
        memory_service=mem_service,
        agent_service=agent_service,
        task_service=task_service,
        max_steps=5,
    )

    run1 = await engine.run_task_reasoning(agent=agent, task=task1, actor=agent_actor)
    assert run1.status == "COMPLETED"

    memories = await mem_service.get_memories_for_agent("org-acme", agent.agent_id)
    assert len(memories) >= 1
    assert "completed" in memories[0].content

    # 4. Test Flow 2: High-risk mutation tool -> HITL WAITING_APPROVAL
    provider_hitl = MockLLMProvider()
    provider_hitl.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.TOOL_CALL,
            selected_tool="employee.get",
            tool_arguments={"employee_id": "emp-bad"},
        )
    )

    # Register employee.terminate tool in ToolRegistry for test
    from backend.agents.tools.domain.enums import ToolCategory
    from backend.agents.tools.domain.models import ToolDefinition

    tool_registry.register_tool(
        ToolDefinition(
            tool_id="employee.terminate",
            name="Terminate Employee",
            description="Terminate employee profile.",
            category=ToolCategory.EMPLOYEE,
            resource="employee",
            action="terminate",
            required_capabilities=["employee:terminate"],
            risk_level="HIGH",
            requires_hitl=True,
            command_type="employee.terminate",
        )
    )

    provider_hitl.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.TOOL_CALL,
            selected_tool="employee.terminate",
            tool_arguments={"employee_id": "emp-bad"},
        )
    )

    task2 = await task_service.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Terminate non-compliant employee",
    )

    engine_hitl = ReasoningEngine(
        provider=provider_hitl,
        tool_gateway=tool_gateway,
        memory_service=mem_service,
        agent_service=agent_service,
        task_service=task_service,
        max_steps=5,
    )

    run2 = await engine_hitl.run_task_reasoning(agent=agent, task=task2, actor=agent_actor)
    assert run2.status == "WAITING_APPROVAL"

    updated_task2 = await task_service.get_task("org-acme", task2.task_id)
    assert updated_task2.status == TaskStatus.WAITING_APPROVAL

    pending_approvals = bus.approval_service.list_pending_for_organization("org-acme")
    assert len(pending_approvals) == 1
