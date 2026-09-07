"""
Workflow Repositories — In-Memory and PostgreSQL Implementations.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from backend.workflows.domain.enums import ExecutionStatus, WorkflowStatus
from backend.workflows.domain.models import (
    DeadLetterJob,
    ScheduledJob,
    StepExecution,
    WorkflowDefinition,
    WorkflowExecution,
)
from backend.workflows.ports.repositories import (
    DeadLetterJobRepositoryPort,
    ScheduledJobRepositoryPort,
    StepExecutionRepositoryPort,
    WorkflowDefinitionRepositoryPort,
    WorkflowExecutionRepositoryPort,
)


class InMemoryWorkflowDefinitionRepository(WorkflowDefinitionRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], WorkflowDefinition] = {}

    async def save(self, workflow_def: WorkflowDefinition) -> WorkflowDefinition:
        self._items[(workflow_def.organization_id, workflow_def.workflow_id)] = workflow_def
        return workflow_def

    async def get_by_id(self, organization_id: str, workflow_id: str) -> WorkflowDefinition | None:
        return self._items.get((organization_id, workflow_id))

    async def list_by_organization(self, organization_id: str) -> Sequence[WorkflowDefinition]:
        return [w for (org, _), w in self._items.items() if org == organization_id]

    async def delete(self, organization_id: str, workflow_id: str) -> bool:
        key = (organization_id, workflow_id)
        if key in self._items:
            del self._items[key]
            return True
        return False


class InMemoryWorkflowExecutionRepository(WorkflowExecutionRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], WorkflowExecution] = {}

    async def save(self, execution: WorkflowExecution) -> WorkflowExecution:
        self._items[(execution.organization_id, execution.execution_id)] = execution
        return execution

    async def get_by_id(self, organization_id: str, execution_id: str) -> WorkflowExecution | None:
        return self._items.get((organization_id, execution_id))

    async def list_by_organization(self, organization_id: str) -> Sequence[WorkflowExecution]:
        return [e for (org, _), e in self._items.items() if org == organization_id]

    async def list_running_executions(self) -> Sequence[WorkflowExecution]:
        return [e for e in self._items.values() if e.status in (WorkflowStatus.RUNNING, WorkflowStatus.WAITING)]


class InMemoryStepExecutionRepository(StepExecutionRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[tuple[str, str, int], StepExecution] = {}

    async def save(self, step_exec: StepExecution) -> StepExecution:
        self._items[(step_exec.execution_id, step_exec.step_id, step_exec.attempt)] = step_exec
        return step_exec

    async def get_by_id(self, execution_id: str, step_id: str) -> StepExecution | None:
        matches = [s for (exec_id, sid, _), s in self._items.items() if exec_id == execution_id and sid == step_id]
        if not matches:
            return None
        # Return latest attempt
        return max(matches, key=lambda x: x.attempt)

    async def list_by_execution(self, execution_id: str) -> Sequence[StepExecution]:
        return [s for (exec_id, _, _), s in self._items.items() if exec_id == execution_id]


class InMemoryScheduledJobRepository(ScheduledJobRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[str, ScheduledJob] = {}

    async def enqueue(self, job: ScheduledJob) -> ScheduledJob:
        self._items[job.job_id] = job
        return job

    async def get_by_id(self, job_id: str) -> ScheduledJob | None:
        return self._items.get(job_id)

    async def acquire_next_job(self, worker_id: str, lease_seconds: int = 60) -> ScheduledJob | None:
        now = datetime.now(tz=UTC)
        for job in self._items.values():
            if job.status == ExecutionStatus.QUEUED:
                job.status = ExecutionStatus.RUNNING
                job.lease_owner = worker_id
                job.lease_until = now + timedelta(seconds=lease_seconds)
                job.attempt_count += 1
                return job
            # Check expired leases
            if job.status == ExecutionStatus.RUNNING and job.lease_until and now > job.lease_until:
                job.lease_owner = worker_id
                job.lease_until = now + timedelta(seconds=lease_seconds)
                job.attempt_count += 1
                return job
        return None

    async def release_job(self, job_id: str) -> None:
        job = self._items.get(job_id)
        if job:
            job.lease_owner = None
            job.lease_until = None

    async def list_queued_jobs(self, organization_id: str) -> Sequence[ScheduledJob]:
        return [j for j in self._items.values() if j.organization_id == organization_id and j.status == ExecutionStatus.QUEUED]


class InMemoryDeadLetterJobRepository(DeadLetterJobRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[str, DeadLetterJob] = {}

    async def save(self, dlq_item: DeadLetterJob) -> DeadLetterJob:
        self._items[dlq_item.job_id] = dlq_item
        return dlq_item

    async def get_by_id(self, job_id: str) -> DeadLetterJob | None:
        return self._items.get(job_id)

    async def list_by_organization(self, organization_id: str) -> Sequence[DeadLetterJob]:
        return [d for d in self._items.values() if d.organization_id == organization_id]

    async def delete(self, job_id: str) -> bool:
        if job_id in self._items:
            del self._items[job_id]
            return True
        return False
