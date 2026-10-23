"""
Workflow Service — Definition Lifecycle Management (Create, Validate, Publish, Enable/Disable, Delete).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.workflows.domain.definitions import validate_workflow_definition
from backend.workflows.domain.exceptions import WorkflowValidationError
from backend.workflows.domain.models import WorkflowDefinition, WorkflowStepDefinition
from backend.workflows.infrastructure.database.repositories import InMemoryWorkflowDefinitionRepository
from backend.workflows.ports.repositories import WorkflowDefinitionRepositoryPort


class WorkflowService:
    """
    Service managing WorkflowDefinition schemas.
    """

    def __init__(self, repository: WorkflowDefinitionRepositoryPort | None = None) -> None:
        self.repository = repository or InMemoryWorkflowDefinitionRepository()

    async def create_workflow_definition(
        self,
        organization_id: str,
        name: str,
        description: str = "",
        steps: list[WorkflowStepDefinition] | None = None,
        trigger_type: str = "MANUAL",
        trigger_config: dict[str, Any] | None = None,
    ) -> WorkflowDefinition:
        """Create a new WorkflowDefinition schema."""
        workflow_def = WorkflowDefinition(
            organization_id=organization_id,
            name=name,
            description=description,
            steps=steps or [],
            trigger_type=trigger_type,  # type: ignore[arg-type]
            trigger_config=trigger_config or {},
            enabled=True,
        )

        validate_workflow_definition(workflow_def)
        return await self.repository.save(workflow_def)

    async def get_workflow_definition(self, organization_id: str, workflow_id: str) -> WorkflowDefinition | None:
        return await self.repository.get_by_id(organization_id, workflow_id)

    async def list_workflows(self, organization_id: str) -> Sequence[WorkflowDefinition]:
        return await self.repository.list_by_organization(organization_id)

    async def enable_workflow(self, organization_id: str, workflow_id: str) -> WorkflowDefinition:
        wf = await self.get_workflow_definition(organization_id, workflow_id)
        if not wf:
            raise WorkflowValidationError(f"Workflow '{workflow_id}' not found.")
        wf.enabled = True
        return await self.repository.save(wf)

    async def disable_workflow(self, organization_id: str, workflow_id: str) -> WorkflowDefinition:
        wf = await self.get_workflow_definition(organization_id, workflow_id)
        if not wf:
            raise WorkflowValidationError(f"Workflow '{workflow_id}' not found.")
        wf.enabled = False
        return await self.repository.save(wf)

    async def delete_workflow(self, organization_id: str, workflow_id: str) -> bool:
        return await self.repository.delete(organization_id, workflow_id)
