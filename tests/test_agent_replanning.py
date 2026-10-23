"""Tests — Replanner handling recoverable failures while rejecting authorization/capability denial bypasses."""

import pytest

from backend.agents.domain.models import Agent, AgentTask
from backend.agents.planning.application.replanner import Replanner
from backend.agents.planning.domain.enums import PlanStatus, StepStatus
from backend.agents.planning.domain.exceptions import ReplanningError
from backend.agents.planning.domain.models import Plan, PlanStep


@pytest.mark.asyncio
async def test_replanner_recoverable_failure_success():
    replanner = Replanner()

    step1 = PlanStep(
        step_id="step-1",
        sequence=1,
        description="Transient network error step",
        tool_name="employee.get",
        status=StepStatus.FAILED,
        failure_reason="Transient HTTP 503 timeout",
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        objective="Fetch employee profile",
        steps=[step1],
    )

    agent = Agent(organization_id="org-acme", name="bot", display_name="Bot", actor_id="actor-1")
    task = AgentTask(organization_id="org-acme", agent_id="agent-1", goal="Fetch profile")

    revised_plan = await replanner.create_revised_plan(plan, agent, task, failure_reason="Transient HTTP 503 timeout")

    assert plan.status == PlanStatus.REPLANNING
    assert revised_plan.version == 2
    assert revised_plan.steps[0].status == StepStatus.PENDING
    assert revised_plan.steps[0].retry_count == 1


@pytest.mark.asyncio
async def test_replanner_rejects_security_policy_denial_bypass():
    replanner = Replanner()

    step1 = PlanStep(
        step_id="step-1",
        sequence=1,
        description="Unauthorized deletion step",
        tool_name="employee.terminate",
        status=StepStatus.FAILED,
        failure_reason="CommandBusExecutionError: Actor is unauthorized for command employee.terminate",
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        objective="Unauthorized termination",
        steps=[step1],
    )

    agent = Agent(organization_id="org-acme", name="bot", display_name="Bot", actor_id="actor-1")
    task = AgentTask(organization_id="org-acme", agent_id="agent-1", goal="Terminate employee")

    with pytest.raises(ReplanningError, match="security policy denial"):
        await replanner.create_revised_plan(
            plan,
            agent,
            task,
            failure_reason="CommandBusExecutionError: Actor is unauthorized for command employee.terminate",
        )

    assert plan.status == PlanStatus.FAILED
    assert "Security denial cannot be bypassed" in plan.failure_reason
