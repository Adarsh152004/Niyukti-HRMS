"""
Event Trigger Processor — EventBus Listener for Event-Driven Workflow Ingestion.

Subscribes to system domain events, matches registered workflow definitions,
and enqueues new WorkflowExecutions while preserving correlation_id, causation_id, and tenant isolation.
"""

from __future__ import annotations

from backend.hrms.domain.actor import Actor, ActorType
from backend.runtime.events import Event, EventBus
from backend.workflows.application.workflow_engine import WorkflowEngine
from backend.workflows.domain.enums import TriggerType, WorkflowStatus
from backend.workflows.domain.models import WorkflowExecution
from backend.workflows.ports.repositories import WorkflowDefinitionRepositoryPort, WorkflowExecutionRepositoryPort


class EventTriggerProcessor:
    """
    Listens for EventBus domain events and triggers matching workflows.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        wf_def_repo: WorkflowDefinitionRepositoryPort | None = None,
        wf_exec_repo: WorkflowExecutionRepositoryPort | None = None,
        workflow_engine: WorkflowEngine | None = None,
    ) -> None:
        self.event_bus = event_bus or EventBus.get_instance()
        self.wf_def_repo = wf_def_repo
        self.wf_exec_repo = wf_exec_repo
        self.workflow_engine = workflow_engine or WorkflowEngine()

    async def handle_event(self, event: Event) -> WorkflowExecution | None:
        """
        Process an incoming domain event, matching workflow triggers.
        """
        org_id = event.payload.get("organization_id") if event.payload else None
        if not org_id and isinstance(event.source, str) and event.source.startswith("org-"):
            org_id = event.source

        if not org_id or not self.wf_def_repo:
            return None

        definitions = await self.wf_def_repo.list_by_organization(org_id)
        matching_def = None
        for wf in definitions:
            if wf.enabled and wf.trigger_type == TriggerType.EVENT:
                trig_evt = wf.trigger_config.get("event_type") or wf.trigger_config.get("event_name")
                if trig_evt == event.event_type:
                    matching_def = wf
                    break

        if not matching_def:
            return None

        # Construct new WorkflowExecution preserving correlation & causation metadata
        execution = WorkflowExecution(
            workflow_id=matching_def.workflow_id,
            organization_id=org_id,
            correlation_id=event.correlation_id or event.event_id,
            causation_id=event.event_id,
            status=WorkflowStatus.READY,
            input_payload=event.payload or {},
        )

        if self.wf_exec_repo:
            await self.wf_exec_repo.save(execution)

        system_actor = Actor(
            actor_id=event.source or "system-event-listener",
            actor_type=ActorType.SYSTEM,
            organization_id=org_id,
        )

        return await self.workflow_engine.execute_workflow(
            workflow_def=matching_def,
            execution=execution,
            actor=system_actor,
        )
