"""Tests — PlanValidator security checks, DAG topological sort, circular dependency rejection, and prohibited tool blocking."""

import pytest

from backend.agents.application.agent_registry import AgentRegistry
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.models import Agent, AgentCapability
from backend.agents.planning.application.plan_validator import PlanValidator
from backend.agents.planning.domain.models import Plan, PlanStep


@pytest.mark.asyncio
async def test_plan_validator_circular_dependency_rejected():
    validator = PlanValidator()

    step1 = PlanStep(
        step_id="step-1",
        sequence=1,
        description="Step 1",
        tool_name="employee.get",
        dependencies=["step-2"],  # Cyclic dependency!
    )
    step2 = PlanStep(
        step_id="step-2",
        sequence=2,
        description="Step 2",
        tool_name="employee.list",
        dependencies=["step-1"],
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        objective="Cyclic plan",
        steps=[step1, step2],
    )

    report = await validator.validate_plan(plan)
    assert not report.valid
    assert any("circular dependency" in err.lower() for err in report.errors)


@pytest.mark.asyncio
async def test_plan_validator_prohibited_tool_rejected():
    validator = PlanValidator()

    step_prohibited = PlanStep(
        sequence=1,
        description="Execute raw database query",
        tool_name="sql.execute",  # Prohibited tool ID!
        arguments={"query": "DELETE FROM employees;"},
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        objective="Malicious plan",
        steps=[step_prohibited],
    )

    report = await validator.validate_plan(plan)
    assert not report.valid
    assert any("prohibited tool" in err.lower() for err in report.all_errors)


@pytest.mark.asyncio
async def test_plan_validator_agent_capability_check():
    registry = AgentRegistry()
    cap_read = AgentCapability(
        capability_id="cap-1",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )

    agent = Agent(
        organization_id="org-acme",
        name="emp-reader",
        display_name="Emp Reader",
        actor_id="actor-1",
        status=AgentStatus.ACTIVE,
        capabilities=[cap_read],
    )
    await registry.register_agent(agent)

    from backend.agents.tools.application.tool_registry import ToolRegistry
    from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools

    tool_reg = ToolRegistry.get_instance()
    register_builtin_tools(tool_reg)

    validator = PlanValidator(registry=registry, tool_registry=tool_reg)

    # Valid step matching agent capability
    valid_step = PlanStep(
        sequence=1,
        description="Get employee",
        tool_name="employee.get",
    )
    # Invalid step requiring capability agent lacks (department.get requires department:read)
    invalid_step = PlanStep(
        sequence=2,
        description="Get department",
        tool_name="department.get",
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        task_id="task-1",
        objective="Mixed plan",
        steps=[valid_step, invalid_step],
    )

    report = await validator.validate_plan(plan, agent=agent)
    assert not report.valid
    assert any("lacks capability" in err.lower() for err in report.all_errors)
