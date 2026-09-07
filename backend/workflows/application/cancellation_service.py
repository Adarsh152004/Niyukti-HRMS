"""
Cancellation & Pause/Resume Service — Controls execution lifecycle state changes.
"""

from __future__ import annotations

from backend.workflows.domain.enums import WorkflowStatus
from backend.workflows.domain.exceptions import WorkflowStateTransitionError
from backend.workflows.domain.models import WorkflowExecution
from backend.workflows.ports.repositories import WorkflowExecutionRepositoryPort


class CancellationService:
    """
    Manages pausing, resuming, and cancelling workflow executions.
    """

    def __init__(self, wf_exec_repo: WorkflowExecutionRepositoryPort) -> None:
        self.wf_exec_repo = wf_exec_repo

    async def pause_execution(self, organization_id: str, execution_id: str) -> WorkflowExecution:
        exec_inst = await self.wf_exec_repo.get_by_id(organization_id, execution_id)
        if not exec_inst:
            raise ValueError(f"Workflow execution '{execution_id}' not found.")
        exec_inst.transition_to(WorkflowStatus.PAUSED)
        return await self.wf_exec_repo.save(exec_inst)

    async def resume_execution(self, organization_id: str, execution_id: str) -> WorkflowExecution:
        exec_inst = await self.wf_exec_repo.get_by_id(organization_id, execution_id)
        if not exec_inst:
            raise ValueError(f"Workflow execution '{execution_id}' not found.")
        exec_inst.transition_to(WorkflowStatus.RUNNING)
        return await self.wf_exec_repo.save(exec_inst)

    async def cancel_execution(self, organization_id: str, execution_id: str) -> WorkflowExecution:
        exec_inst = await self.wf_exec_repo.get_by_id(organization_id, execution_id)
        if not exec_inst:
            raise ValueError(f"Workflow execution '{execution_id}' not found.")
        if exec_inst.status == WorkflowStatus.COMPLETED:
            raise WorkflowStateTransitionError("Completed workflow execution cannot be cancelled.")
        exec_inst.transition_to(WorkflowStatus.CANCELLED)
        return await self.wf_exec_repo.save(exec_inst)
