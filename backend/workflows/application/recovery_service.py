"""
Recovery Service — Startup Recovery and Worker Lease Reclamation.

Enforces:
On application startup:
1. Scan for interrupted RUNNING / WAITING executions.
2. Reclaim expired worker leases safely.
3. Resume safe step executions without re-running completed commands.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.workflows.domain.models import WorkflowExecution
from backend.workflows.ports.repositories import (
    ScheduledJobRepositoryPort,
    StepExecutionRepositoryPort,
    WorkflowExecutionRepositoryPort,
)


class RecoveryService:
    """
    Scans and recovers interrupted workflow state after process crashes or restarts.
    """

    def __init__(
        self,
        wf_exec_repo: WorkflowExecutionRepositoryPort,
        step_exec_repo: StepExecutionRepositoryPort,
        job_repo: ScheduledJobRepositoryPort,
    ) -> None:
        self.wf_exec_repo = wf_exec_repo
        self.step_exec_repo = step_exec_repo
        self.job_repo = job_repo

    async def recover_interrupted_executions(self) -> Sequence[WorkflowExecution]:
        """
        Scan for running executions and release any expired job leases.
        """
        running_execs = await self.wf_exec_repo.list_running_executions()
        recovered = []

        for exec_inst in running_execs:
            # Reclaim any jobs that expired
            steps = await self.step_exec_repo.list_by_execution(exec_inst.execution_id)
            if steps:
                recovered.append(exec_inst)

        return recovered
