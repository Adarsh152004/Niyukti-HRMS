"""Tests — Plan and PlanStep domain models and PlannerService."""

import pytest

from backend.agents.planning.application.planner_service import PlannerService
from backend.agents.planning.domain.enums import PlanStatus, StepStatus
from backend.agents.planning.domain.models import Plan, PlanStep


@pytest.mark.asyncio
async def test_plan_instantiation_and_defaults():
    step1 = PlanStep(
        sequence=1,
        description="Get employee details",
        tool_name="employee.get",
        command_type="employee.read",
        arguments={"employee_id": "emp-100"},
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        objective="Read employee profile",
        steps=[step1],
    )

    assert plan.status == PlanStatus.DRAFT
    assert plan.version == 1
    assert len(plan.steps) == 1
    assert plan.steps[0].status == StepStatus.PENDING


@pytest.mark.asyncio
async def test_planner_service_create_and_retrieve_plan():
    from backend.agents.application.agent_service import AgentService
    from backend.agents.domain.models import AgentCapability

    agent_svc = AgentService()
    planner = PlannerService(agent_service=agent_svc)
    cap_list = AgentCapability(capability_id="cap-list", name="List Emp", resource="employee", actions=["read", "list"])
    agent = await agent_svc.create_agent(
        organization_id="org-acme",
        name="agent-1",
        display_name="Agent 1",
        capabilities=[cap_list],
    )
    await agent_svc.activate_agent("org-acme", agent.agent_id)

    step1 = PlanStep(
        sequence=1,
        description="List employees",
        tool_name="employee.list",
        command_type="employee.list",
    )

    plan = await planner.create_plan(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        task_id="task-1",
        objective="List department employees",
        steps=[step1],
    )

    assert plan.status == PlanStatus.READY

    retrieved = await planner.get_plan("org-acme", plan.plan_id)
    assert retrieved is not None
    assert retrieved.objective == "List department employees"
