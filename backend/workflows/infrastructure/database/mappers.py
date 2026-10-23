"""
Workflow Domain ↕ Database Mappers.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.workflows.domain.enums import (
    ErrorCategory,
    ExecutionStatus,
    Priority,
    StepStatus,
    TriggerType,
    WorkflowStatus,
)
from backend.workflows.domain.models import (
    DeadLetterJob,
    ScheduledJob,
    StepExecution,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStepDefinition,
)
from backend.workflows.infrastructure.database.models import (
    DeadLetterJobModel,
    ScheduledJobModel,
    StepExecutionModel,
    WorkflowDefinitionModel,
    WorkflowExecutionModel,
)


class WorkflowDefinitionMapper:
    @staticmethod
    def to_domain(model: WorkflowDefinitionModel) -> WorkflowDefinition:
        now = datetime.now(tz=UTC)
        steps = [WorkflowStepDefinition(**s) for s in (model.steps_json or [])]
        return WorkflowDefinition(
            workflow_id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            description=model.description,
            version=model.version,
            trigger_type=TriggerType(model.trigger_type),
            trigger_config=model.trigger_config_json or {},
            steps=steps,
            enabled=model.enabled,
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: WorkflowDefinition) -> WorkflowDefinitionModel:
        steps_json = [s.model_dump() for s in domain.steps]
        return WorkflowDefinitionModel(
            id=domain.workflow_id,
            organization_id=domain.organization_id,
            name=domain.name,
            description=domain.description,
            version=domain.version,
            trigger_type=domain.trigger_type.value,
            trigger_config_json=domain.trigger_config,
            steps_json=steps_json,
            enabled=domain.enabled,
        )


class WorkflowExecutionMapper:
    @staticmethod
    def to_domain(model: WorkflowExecutionModel) -> WorkflowExecution:
        return WorkflowExecution(
            execution_id=model.id,
            workflow_id=model.workflow_id,
            organization_id=model.organization_id,
            correlation_id=model.correlation_id,
            causation_id=model.causation_id,
            status=WorkflowStatus(model.status),
            current_step=model.current_step,
            input_payload=model.input_payload_json or {},
            output_payload=model.output_payload_json or {},
            started_at=model.started_at,
            completed_at=model.completed_at,
            failure_reason=model.failure_reason,
            attempt_count=model.attempt_count,
        )

    @staticmethod
    def to_model(domain: WorkflowExecution) -> WorkflowExecutionModel:
        return WorkflowExecutionModel(
            id=domain.execution_id,
            workflow_id=domain.workflow_id,
            organization_id=domain.organization_id,
            correlation_id=domain.correlation_id,
            causation_id=domain.causation_id,
            status=domain.status.value,
            current_step=domain.current_step,
            input_payload_json=domain.input_payload,
            output_payload_json=domain.output_payload,
            started_at=domain.started_at,
            completed_at=domain.completed_at,
            failure_reason=domain.failure_reason,
            attempt_count=domain.attempt_count,
        )


class StepExecutionMapper:
    @staticmethod
    def to_domain(model: StepExecutionModel) -> StepExecution:
        return StepExecution(
            execution_id=model.execution_id,
            step_id=model.step_id,
            status=StepStatus(model.status),
            attempt=model.attempt,
            started_at=model.started_at,
            completed_at=model.completed_at,
            output=model.output_json or {},
            error=model.error,
            next_retry_at=model.next_retry_at,
        )

    @staticmethod
    def to_model(domain: StepExecution) -> StepExecutionModel:
        return StepExecutionModel(
            id=f"{domain.execution_id}-{domain.step_id}-{domain.attempt}",
            execution_id=domain.execution_id,
            step_id=domain.step_id,
            status=domain.status.value,
            attempt=domain.attempt,
            started_at=domain.started_at,
            completed_at=domain.completed_at,
            output_json=domain.output,
            error=domain.error,
            next_retry_at=domain.next_retry_at,
        )


class ScheduledJobMapper:
    @staticmethod
    def to_domain(model: ScheduledJobModel) -> ScheduledJob:
        now = datetime.now(tz=UTC)
        return ScheduledJob(
            job_id=model.id,
            organization_id=model.organization_id,
            workflow_id=model.workflow_id,
            execution_id=model.execution_id,
            step_id=model.step_id,
            scheduled_at=model.scheduled_at,
            priority=Priority(model.priority),
            status=ExecutionStatus(model.status),
            attempt_count=model.attempt_count,
            max_attempts=model.max_attempts,
            lease_owner=model.lease_owner,
            lease_until=model.lease_until,
            payload=model.payload_json or {},
            created_at=model.created_at or now,
        )

    @staticmethod
    def to_model(domain: ScheduledJob) -> ScheduledJobModel:
        return ScheduledJobModel(
            id=domain.job_id,
            organization_id=domain.organization_id,
            workflow_id=domain.workflow_id,
            execution_id=domain.execution_id,
            step_id=domain.step_id,
            scheduled_at=domain.scheduled_at,
            priority=domain.priority.value,
            status=domain.status.value,
            attempt_count=domain.attempt_count,
            max_attempts=domain.max_attempts,
            lease_owner=domain.lease_owner,
            lease_until=domain.lease_until,
            payload_json=domain.payload,
        )


class DeadLetterJobMapper:
    @staticmethod
    def to_domain(model: DeadLetterJobModel) -> DeadLetterJob:
        return DeadLetterJob(
            job_id=model.id,
            execution_id=model.execution_id,
            workflow_id=model.workflow_id,
            organization_id=model.organization_id,
            failure_reason=model.failure_reason,
            error_category=ErrorCategory(model.error_category),
            payload=model.payload_json or {},
            failed_at=model.failed_at,
            retry_count=model.retry_count,
            metadata=model.metadata_json or {},
        )

    @staticmethod
    def to_model(domain: DeadLetterJob) -> DeadLetterJobModel:
        return DeadLetterJobModel(
            id=domain.job_id,
            execution_id=domain.execution_id,
            workflow_id=domain.workflow_id,
            organization_id=domain.organization_id,
            failure_reason=domain.failure_reason,
            error_category=domain.error_category.value,
            payload_json=domain.payload,
            failed_at=domain.failed_at,
            retry_count=domain.retry_count,
            metadata_json=domain.metadata,
        )
