"""
Workflow CLI Foundation — Command Line Interface for Workflow Definitions, Executions, and DLQ.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.workflows.application.workflow_service import WorkflowService
from backend.workflows.domain.models import DeadLetterJob, WorkflowDefinition, WorkflowExecution
from backend.workflows.infrastructure.database.repositories import (
    InMemoryDeadLetterJobRepository,
    InMemoryWorkflowExecutionRepository,
)


class WorkflowCLI:
    """
    CLI interface managing Workflow Definitions, Executions, and DLQ.
    """

    def __init__(
        self,
        wf_service: WorkflowService | None = None,
        wf_exec_repo: InMemoryWorkflowExecutionRepository | None = None,
        dlq_repo: InMemoryDeadLetterJobRepository | None = None,
    ) -> None:
        self.wf_service = wf_service or WorkflowService()
        self.wf_exec_repo = wf_exec_repo or InMemoryWorkflowExecutionRepository()
        self.dlq_repo = dlq_repo or InMemoryDeadLetterJobRepository()

    async def list_workflows(self, organization_id: str) -> Sequence[WorkflowDefinition]:
        """List all workflow definitions for tenant."""
        return await self.wf_service.list_workflows(organization_id)

    async def inspect_workflow(self, organization_id: str, workflow_id: str) -> WorkflowDefinition | None:
        """Inspect workflow definition details."""
        return await self.wf_service.get_workflow_definition(organization_id, workflow_id)

    async def list_executions(self, organization_id: str) -> Sequence[WorkflowExecution]:
        """List workflow executions for tenant."""
        return await self.wf_exec_repo.list_by_organization(organization_id)

    async def list_dlq(self, organization_id: str) -> Sequence[DeadLetterJob]:
        """List dead letter queue items for tenant."""
        return await self.dlq_repo.list_by_organization(organization_id)
