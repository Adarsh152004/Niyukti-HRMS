"""
Workflow Domain Events — Lifecycle events published during workflow DAG execution.
"""

from __future__ import annotations

from backend.hrms.domain.events import DomainEvent


class WorkflowCreated(DomainEvent):
    event_type: str = "WorkflowCreated"


class WorkflowPublished(DomainEvent):
    event_type: str = "WorkflowPublished"


class WorkflowStarted(DomainEvent):
    event_type: str = "WorkflowStarted"


class WorkflowStepStarted(DomainEvent):
    event_type: str = "WorkflowStepStarted"


class WorkflowStepWaiting(DomainEvent):
    event_type: str = "WorkflowStepWaiting"


class WorkflowStepApprovalRequired(DomainEvent):
    event_type: str = "WorkflowStepApprovalRequired"


class WorkflowStepSucceeded(DomainEvent):
    event_type: str = "WorkflowStepSucceeded"


class WorkflowStepFailed(DomainEvent):
    event_type: str = "WorkflowStepFailed"


class WorkflowStepRetrying(DomainEvent):
    event_type: str = "WorkflowStepRetrying"


class WorkflowCompleted(DomainEvent):
    event_type: str = "WorkflowCompleted"


class WorkflowFailed(DomainEvent):
    event_type: str = "WorkflowFailed"


class WorkflowCancelled(DomainEvent):
    event_type: str = "WorkflowCancelled"


class WorkflowDeadLettered(DomainEvent):
    event_type: str = "WorkflowDeadLettered"
