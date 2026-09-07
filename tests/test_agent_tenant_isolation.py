"""Tests — Strict Tenant Isolation across Agent Plans, Tasks, Executions, and Memory."""

import pytest

from backend.agents.application.agent_registry import AgentRegistry
from backend.agents.application.agent_service import AgentService
from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.exceptions import AgentNotFoundError, AgentTaskError
from backend.agents.domain.models import Agent, AgentCapability
from backend.agents.orchestration.application.orchestrator import AgentOrchestrator
from backend.agents.planning.application.planner_service import PlannerService
from backend.agents.planning.domain.models import PlanStep


@pytest.mark.asyncio
async def test_cross_tenant_plan_access_denied():
    agent_svc = AgentService()
    planner = PlannerService(agent_service=agent_svc)
    cap_read = AgentCapability(capability_id="cap-read", name="Read Emp", resource="employee", actions=["read"])
    agent_a = await agent_svc.create_agent(
        organization_id="org-tenant-a",
        name="agent-a",
        display_name="Agent A",
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-tenant-a", agent_a.agent_id)

    step = PlanStep(sequence=1, description="Read emp", tool_name="employee.get")

    plan = await planner.create_plan(
        organization_id="org-tenant-a",
        agent_id=agent_a.agent_id,
        task_id="task-a",
        objective="Tenant A plan",
        steps=[step],
    )

    # Attempt to fetch Tenant A plan under Tenant B organization returns None
    result = await planner.get_plan("org-tenant-b", plan.plan_id)
    assert result is None


@pytest.mark.asyncio
async def test_cross_tenant_task_orchestration_denied():
    registry = AgentRegistry()
    task_svc = AgentTaskService()
    orchestrator = AgentOrchestrator(registry=registry, task_service=task_svc)

    agent_a = Agent(
        organization_id="org-tenant-a", name="agent-a", display_name="Agent A", actor_id="actor-a", status=AgentStatus.ACTIVE
    )
    await registry.register_agent(agent_a)

    task_a = await task_svc.create_task(organization_id="org-tenant-a", agent_id=agent_a.agent_id, goal="Goal A")

    # Tenant B attempting to run Tenant A's task raises AgentNotFoundError or AgentTaskError
    with pytest.raises((AgentTaskError, AgentNotFoundError)):
        await orchestrator.run_task("org-tenant-b", agent_a.agent_id, task_a.task_id)
