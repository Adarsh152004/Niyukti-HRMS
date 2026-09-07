"""Tests — RecoveryManager crash recovery without duplicating completed commands."""

import pytest

from backend.agents.orchestration.application.recovery_manager import RecoveryManager
from backend.agents.orchestration.domain.enums import ExecutionState
from backend.agents.orchestration.domain.models import AgentExecution
from backend.agents.planning.domain.enums import PlanStatus, StepStatus
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.agents.planning.infrastructure.database.repositories import InMemoryPlanRepository


@pytest.mark.asyncio
async def test_recovery_manager_resumes_interrupted_execution():
    plan_repo = InMemoryPlanRepository()
    recovery_mgr = RecoveryManager(plan_repo=plan_repo)

    step1 = PlanStep(
        step_id="step-1",
        sequence=1,
        description="Completed step",
        tool_name="employee.get",
        status=StepStatus.COMPLETED,
        result={"command_id": "cmd-1", "status": "SUCCESS"},
    )
    step2 = PlanStep(
        step_id="step-2",
        sequence=2,
        description="Interrupted step during crash",
        tool_name="employee.list",
        status=StepStatus.EXECUTING,
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        status=PlanStatus.EXECUTING,
        objective="Multi step task",
        steps=[step1, step2],
    )
    await plan_repo.save_plan(plan)

    execution = AgentExecution(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        plan_id=plan.plan_id,
        state=ExecutionState.EXECUTING,
    )

    interrupted = await recovery_mgr.find_interrupted_executions([execution])
    assert len(interrupted) == 1

    recovered = await recovery_mgr.recover_execution(interrupted[0], plan_repo)
    assert recovered.state == ExecutionState.PAUSED

    # Verify step1 remains COMPLETED (not re-executed) and step2 reset to PENDING
    updated_plan = await plan_repo.get_plan("org-acme", plan.plan_id)
    assert updated_plan.steps[0].status == StepStatus.COMPLETED
    assert updated_plan.steps[1].status == StepStatus.PENDING
