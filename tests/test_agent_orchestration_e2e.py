"""Tests — Complete End-to-End Agent Orchestration scenario and malicious reasoning output rejection."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.application.command_gateway import AgentCommandGateway
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentType, TaskStatus
from backend.agents.domain.models import AgentCapability
from backend.agents.memory.application.memory_service import MemoryService
from backend.agents.orchestration.application.orchestrator import AgentOrchestrator
from backend.agents.planning.application.plan_validator import PlanValidator
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import ReasoningDecision
from backend.agents.reasoning.providers.mock import MockLLMProvider
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools
from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import (
    GetEmployeeCommandHandler,
    UpdateEmployeeCommandHandler,
)
from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_end_to_end_agent_orchestration_scenario():
    # 1. Setup CommandBus, ToolRegistry, Services
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
    bus.registry.register(
        "employee.update",
        UpdateEmployeeCommandHandler(),
        CommandMetadata(
            command_type="employee.update",
            description="Update employee",
            required_permissions=["EMPLOYEE_WRITE"],
            risk_level=RiskLevel.MEDIUM,
        ),
    )

    tool_registry = ToolRegistry()
    register_builtin_tools(tool_registry)

    cmd_gateway = AgentCommandGateway(command_bus=bus)
    tool_gateway = ToolExecutionGateway(registry=tool_registry, command_gateway=cmd_gateway)

    agent_svc = AgentService()
    task_svc = AgentTaskService()
    mem_svc = MemoryService()

    cap_read = AgentCapability(capability_id="cap-read", name="Read Emp", resource="employee", actions=["read"])
    cap_update = AgentCapability(capability_id="cap-update", name="Update Emp", resource="employee", actions=["update"])

    agent = await agent_svc.create_agent(
        organization_id="org-acme",
        name="hr-update-agent",
        display_name="HR Update Agent",
        agent_type=AgentType.HR_AGENT,
        capabilities=[cap_read, cap_update],
    )
    await agent_svc.activate_agent("org-acme", agent.agent_id)

    agent_actor = Actor(
        actor_id=agent.actor_id,
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions={"EMPLOYEE_READ", "EMPLOYEE_WRITE"},
    )

    provider = MockLLMProvider()
    provider.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.TOOL_CALL,
            selected_tool="employee.get",
            tool_arguments={"employee_id": "emp-101"},
        )
    )
    provider.enqueue_decision(
        ReasoningDecision(
            decision_type=DecisionType.ANSWER,
            explanation="Found employee and updated department.",
            final_response="Employee emp-101 department updated to Engineering.",
        )
    )

    task = await task_svc.create_task(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        goal="Find employee emp-101 and update department to Engineering",
    )

    reasoning_engine = ReasoningEngine(
        provider=provider,
        tool_gateway=tool_gateway,
        memory_service=mem_svc,
        agent_service=agent_svc,
        task_service=task_svc,
    )

    orchestrator = AgentOrchestrator(
        registry=agent_svc.registry,
        agent_service=agent_svc,
        task_service=task_svc,
        reasoning_engine=reasoning_engine,
        tool_gateway=tool_gateway,
        memory_service=mem_svc,
    )

    execution = await orchestrator.run_task("org-acme", agent.agent_id, task.task_id, actor=agent_actor)

    assert execution.state == "COMPLETED"
    assert "Engineering" in execution.result_data["final_response"]

    # Verify task state
    updated_task = await task_svc.get_task("org-acme", task.task_id)
    assert updated_task.status == TaskStatus.COMPLETED

    # Verify memory recorded
    memories = await mem_svc.get_memories_for_agent("org-acme", agent.agent_id)
    assert len(memories) >= 1


@pytest.mark.asyncio
async def test_malicious_reasoning_attempts_rejected():
    validator = PlanValidator()

    # Attempt 1: Raw SQL execution
    sql_step = PlanStep(sequence=1, description="Raw SQL", tool_name="sql.execute", arguments={"query": "DROP TABLE employees;"})
    plan_sql = Plan(organization_id="org-acme", agent_id="agent-1", task_id="task-1", objective="SQL Injection", steps=[sql_step])
    report_sql = await validator.validate_plan(plan_sql)
    assert not report_sql.valid

    # Attempt 2: Tenant change / cross-tenant payload modification
    tenant_step = PlanStep(
        sequence=1,
        description="Cross tenant update",
        tool_name="employee.get",
        command_type="employee.read",
        arguments={"organization_id": "org-ATTACKER"},
    )
    plan_tenant = Plan(
        organization_id="org-VICTIM", agent_id="agent-1", task_id="task-1", objective="Cross tenant", steps=[tenant_step]
    )
    report_tenant = await validator.validate_plan(plan_tenant)
    assert not report_tenant.valid
    assert any("Cross-tenant payload modification" in err for err in report_tenant.errors)
