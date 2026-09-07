"""
RecoveryManager — Crash Recovery Manager for Agent Orchestration trajectories.
Scans for interrupted execution states on startup and resumes them safely without duplicating completed commands.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.agents.orchestration.domain.enums import ExecutionState
from backend.agents.orchestration.domain.models import AgentExecution
from backend.agents.planning.domain.enums import PlanStatus, StepStatus
from backend.agents.planning.ports.repositories import PlanRepositoryPort

logger = logging.getLogger(__name__)


class RecoveryManager:
    """
    Recovers interrupted agent executions upon system crash or startup.
    """

    def __init__(self, plan_repo: PlanRepositoryPort | None = None) -> None:
        self.plan_repo = plan_repo

    async def find_interrupted_executions(self, executions: Sequence[AgentExecution]) -> list[AgentExecution]:
        """Filter executions left in non-terminal interrupted states."""
        interrupted_states = [
            ExecutionState.EXECUTING,
            ExecutionState.PLANNING,
            ExecutionState.VALIDATING,
            ExecutionState.REPLANNING,
        ]
        return [e for e in executions if e.state in interrupted_states]

    async def recover_execution(self, execution: AgentExecution, plan_repo: PlanRepositoryPort) -> AgentExecution:
        """
        Recover single interrupted execution safely.
        """
        if not execution.plan_id:
            execution.state = ExecutionState.FAILED
            execution.failure_reason = "Crash recovery: Missing plan reference."
            return execution

        plan = await plan_repo.get_plan(execution.organization_id, execution.plan_id)
        if not plan:
            execution.state = ExecutionState.FAILED
            execution.failure_reason = f"Crash recovery: Plan '{execution.plan_id}' not found."
            return execution

        # Find any step left in EXECUTING state during crash
        for step in plan.steps:
            if step.status == StepStatus.EXECUTING:
                if step.result and "command_id" in step.result:
                    step.status = StepStatus.COMPLETED
                else:
                    step.status = StepStatus.PENDING

        if plan.status == PlanStatus.EXECUTING:
            execution.state = ExecutionState.PAUSED
            logger.info(f"Execution '{execution.execution_id}' safely recovered to PAUSED state.")

        await plan_repo.save_plan(plan)
        return execution
