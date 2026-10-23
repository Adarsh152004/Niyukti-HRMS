"""
Workflow Domain — Core Entities for Definitions, Steps, Executions, Scheduled Jobs, and Dead Letter Items.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.workflows.domain.enums import (
    ErrorCategory,
    ExecutionStatus,
    Priority,
    RetryStrategy,
    StepStatus,
    TriggerType,
    WorkflowStatus,
)
from backend.workflows.domain.exceptions import WorkflowStateTransitionError


def generate_wf_id(prefix: str = "wf") -> str:
    """Generate prefixed random UUID for workflow entities."""
    return f"{prefix}-{uuid.uuid4()}"


class WorkflowStepDefinition(BaseModel):
    """
    Definition of an individual step in a workflow DAG.
    Each step maps to a CommandBus command type.
    """

    step_id: str = Field(description="Step identifier unique within workflow e.g. step_create_emp")
    workflow_id: str = Field(description="Parent workflow definition ID")
    name: str = Field(description="Human readable step title")
    command_type: str = Field(description="CommandBus command type e.g. employee.create")
    command_payload: dict[str, Any] = Field(default_factory=dict, description="Command payload template")
    dependencies: list[str] = Field(
        default_factory=list,
        description="IDs of prerequisite steps that must succeed before this step can execute",
    )
    timeout_seconds: int = Field(default=300, description="Step timeout limit in seconds")
    retry_policy: dict[str, Any] = Field(
        default_factory=lambda: {
            "strategy": RetryStrategy.EXPONENTIAL.value,
            "max_attempts": 3,
            "initial_interval_seconds": 2,
            "max_interval_seconds": 60,
            "backoff_multiplier": 2.0,
            "jitter": True,
        }
    )
    risk_override: str | None = Field(default=None)
    requires_approval: bool = Field(default=False)
    condition: str | None = Field(default=None, description="Optional payload expression for conditional step execution")
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    """
    Definition schema representing a reusable Workflow DAG.
    """

    workflow_id: str = Field(default_factory=lambda: generate_wf_id("wf_def"))
    organization_id: str = Field(description="Tenant boundary")
    name: str = Field(description="Workflow title e.g. Employee Onboarding Workflow")
    description: str = Field(default="")
    version: int = Field(default=1)
    trigger_type: TriggerType = Field(default=TriggerType.MANUAL)
    trigger_config: dict[str, Any] = Field(default_factory=dict, description="Trigger configuration e.g. event_name or CRON expr")
    priority: Priority = Field(default=Priority.NORMAL)
    steps: list[WorkflowStepDefinition] = Field(default_factory=list)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class StepExecution(BaseModel):
    """
    Runtime execution state of a workflow step.
    """

    execution_id: str = Field(description="Parent WorkflowExecution ID")
    step_id: str = Field(description="Step ID within workflow definition")
    command_type: str = Field(default="", description="CommandBus command type executed")
    status: StepStatus = Field(default=StepStatus.PENDING)
    attempt: int = Field(default=1)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    output: dict[str, Any] = Field(default_factory=dict)
    output_payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = Field(default=None)
    next_retry_at: datetime | None = Field(default=None)


class WorkflowExecution(BaseModel):
    """
    Runtime instance of an executing Workflow.
    """

    execution_id: str = Field(default_factory=lambda: generate_wf_id("wf_exec"))
    workflow_id: str = Field(description="Parent WorkflowDefinition ID")
    organization_id: str = Field(description="Tenant boundary")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: WorkflowStatus = Field(default=WorkflowStatus.READY)
    current_step: str | None = Field(default=None)
    input_payload: dict[str, Any] = Field(default_factory=dict)
    output_payload: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = Field(default=None)
    failure_reason: str | None = Field(default=None)
    attempt_count: int = Field(default=1)

    def transition_to(self, new_status: WorkflowStatus) -> None:
        """
        Validate and enforce state machine transitions for WorkflowExecution.
        """
        allowed: dict[WorkflowStatus, set[WorkflowStatus]] = {
            WorkflowStatus.DRAFT: {WorkflowStatus.READY, WorkflowStatus.CANCELLED},
            WorkflowStatus.READY: {WorkflowStatus.RUNNING, WorkflowStatus.PAUSED, WorkflowStatus.CANCELLED},
            WorkflowStatus.RUNNING: {
                WorkflowStatus.WAITING,
                WorkflowStatus.WAITING_APPROVAL,
                WorkflowStatus.PAUSED,
                WorkflowStatus.COMPLETED,
                WorkflowStatus.FAILED,
                WorkflowStatus.CANCELLED,
            },
            WorkflowStatus.WAITING: {WorkflowStatus.RUNNING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED},
            WorkflowStatus.WAITING_APPROVAL: {WorkflowStatus.RUNNING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED},
            WorkflowStatus.PAUSED: {WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
            WorkflowStatus.FAILED: {WorkflowStatus.READY, WorkflowStatus.EXPIRED},
            WorkflowStatus.COMPLETED: set(),
            WorkflowStatus.CANCELLED: set(),
            WorkflowStatus.EXPIRED: set(),
        }

        if self.status == new_status:
            return

        valid_next = allowed.get(self.status, set())
        if new_status not in valid_next:
            raise WorkflowStateTransitionError(
                f"Invalid workflow execution transition from '{self.status.value}' to '{new_status.value}'."
            )
        self.status = new_status


class ScheduledJob(BaseModel):
    """
    Durable job queued or scheduled for background execution.
    Includes worker lease fields for concurrency locking.
    """

    job_id: str = Field(default_factory=lambda: generate_wf_id("job"))
    organization_id: str = Field(description="Tenant boundary")
    workflow_id: str
    execution_id: str
    step_id: str | None = Field(default=None)
    scheduled_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    priority: Priority = Field(default=Priority.NORMAL)
    status: ExecutionStatus = Field(default=ExecutionStatus.QUEUED)
    attempt_count: int = Field(default=0)
    max_attempts: int = Field(default=3)
    lease_owner: str | None = Field(default=None)
    lease_until: datetime | None = Field(default=None)
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class DeadLetterJob(BaseModel):
    """
    Job record moved to Dead Letter Queue after max retries or unrecoverable error.
    """

    job_id: str = Field(default_factory=lambda: generate_wf_id("dlq"))
    execution_id: str
    workflow_id: str
    organization_id: str
    failure_reason: str
    error_category: ErrorCategory = Field(default=ErrorCategory.NON_RETRYABLE)
    payload: dict[str, Any] = Field(default_factory=dict)
    failed_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    retry_count: int = Field(default=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
