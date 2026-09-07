"""
Workflow Ports — Abstract Repository Interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.workflows.domain.models import (
    DeadLetterJob,
    ScheduledJob,
    StepExecution,
    WorkflowDefinition,
    WorkflowExecution,
)


class WorkflowDefinitionRepositoryPort(ABC):
    @abstractmethod
    async def save(self, workflow_def: WorkflowDefinition) -> WorkflowDefinition:
        pass

    @abstractmethod
    async def get_by_id(self, organization_id: str, workflow_id: str) -> WorkflowDefinition | None:
        pass

    @abstractmethod
    async def list_by_organization(self, organization_id: str) -> Sequence[WorkflowDefinition]:
        pass

    @abstractmethod
    async def delete(self, organization_id: str, workflow_id: str) -> bool:
        pass


class WorkflowExecutionRepositoryPort(ABC):
    @abstractmethod
    async def save(self, execution: WorkflowExecution) -> WorkflowExecution:
        pass

    @abstractmethod
    async def get_by_id(self, organization_id: str, execution_id: str) -> WorkflowExecution | None:
        pass

    @abstractmethod
    async def list_by_organization(self, organization_id: str) -> Sequence[WorkflowExecution]:
        pass

    @abstractmethod
    async def list_running_executions(self) -> Sequence[WorkflowExecution]:
        pass


class StepExecutionRepositoryPort(ABC):
    @abstractmethod
    async def save(self, step_exec: StepExecution) -> StepExecution:
        pass

    @abstractmethod
    async def get_by_id(self, execution_id: str, step_id: str) -> StepExecution | None:
        pass

    @abstractmethod
    async def list_by_execution(self, execution_id: str) -> Sequence[StepExecution]:
        pass


class ScheduledJobRepositoryPort(ABC):
    @abstractmethod
    async def enqueue(self, job: ScheduledJob) -> ScheduledJob:
        pass

    @abstractmethod
    async def get_by_id(self, job_id: str) -> ScheduledJob | None:
        pass

    @abstractmethod
    async def acquire_next_job(self, worker_id: str, lease_seconds: int = 60) -> ScheduledJob | None:
        pass

    @abstractmethod
    async def release_job(self, job_id: str) -> None:
        pass

    @abstractmethod
    async def list_queued_jobs(self, organization_id: str) -> Sequence[ScheduledJob]:
        pass


class DeadLetterJobRepositoryPort(ABC):
    @abstractmethod
    async def save(self, dlq_item: DeadLetterJob) -> DeadLetterJob:
        pass

    @abstractmethod
    async def get_by_id(self, job_id: str) -> DeadLetterJob | None:
        pass

    @abstractmethod
    async def list_by_organization(self, organization_id: str) -> Sequence[DeadLetterJob]:
        pass

    @abstractmethod
    async def delete(self, job_id: str) -> bool:
        pass
