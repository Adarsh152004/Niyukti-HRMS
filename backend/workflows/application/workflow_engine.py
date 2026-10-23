"""
WorkflowEngine — Core Orchestrator for DAG Execution, Retry/Backoff, DLQ, and Lifecycle Events.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from backend.hrms.domain.actor import Actor
from backend.runtime.events import Event, EventBus
from backend.workflows.application.retry_service import RetryService
from backend.workflows.application.step_executor import StepExecutor
from backend.workflows.application.timeout_service import TimeoutService
from backend.workflows.domain.definitions import get_execution_order, validate_workflow_definition
from backend.workflows.domain.enums import StepStatus, WorkflowStatus
from backend.workflows.domain.models import (
    DeadLetterJob,
    StepExecution,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStepDefinition,
)
from backend.workflows.ports.repositories import (
    DeadLetterJobRepositoryPort,
    StepExecutionRepositoryPort,
    WorkflowDefinitionRepositoryPort,
    WorkflowExecutionRepositoryPort,
)


class WorkflowEngine:
    """
    Core Workflow DAG Execution Engine.
    """

    def __init__(
        self,
        step_executor: StepExecutor | None = None,
        retry_service: RetryService | None = None,
        timeout_service: TimeoutService | None = None,
        event_bus: EventBus | None = None,
        wf_def_repo: WorkflowDefinitionRepositoryPort | None = None,
        wf_exec_repo: WorkflowExecutionRepositoryPort | None = None,
        step_exec_repo: StepExecutionRepositoryPort | None = None,
        dlq_repo: DeadLetterJobRepositoryPort | None = None,
    ) -> None:
        self.step_executor = step_executor or StepExecutor()
        self.retry_service = retry_service or RetryService()
        self.timeout_service = timeout_service or TimeoutService()
        self.event_bus = event_bus or EventBus.get_instance()

        self.wf_def_repo = wf_def_repo
        self.wf_exec_repo = wf_exec_repo
        self.step_exec_repo = step_exec_repo
        self.dlq_repo = dlq_repo

    async def execute_workflow(
        self,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        actor: Actor,
    ) -> WorkflowExecution:
        """
        Execute a Workflow DAG.
        Resolves topological step dependencies and executes ready steps concurrently where safe.
        """
        validate_workflow_definition(workflow_def)
        execution.transition_to(WorkflowStatus.RUNNING)
        if self.wf_exec_repo:
            await self.wf_exec_repo.save(execution)

        # Emit WorkflowStarted Event
        await self.event_bus.publish(
            Event(
                event_type="hrms.workflow.started",
                source=actor.actor_id,
                payload={
                    "workflow_id": workflow_def.workflow_id,
                    "execution_id": execution.execution_id,
                    "organization_id": execution.organization_id,
                },
                correlation_id=execution.correlation_id,
            )
        )

        step_statuses: dict[str, StepStatus] = {s.step_id: StepStatus.PENDING for s in workflow_def.steps}

        execution_levels = get_execution_order(workflow_def)

        for level in execution_levels:
            if execution.status in (WorkflowStatus.FAILED, WorkflowStatus.CANCELLED, WorkflowStatus.PAUSED):
                break

            # Execute all ready steps in current topological level concurrently
            tasks = []
            for step_def in level:
                # Check dependencies succeeded
                deps_ok = all(step_statuses.get(d) == StepStatus.SUCCEEDED for d in step_def.dependencies)
                if not deps_ok:
                    step_statuses[step_def.step_id] = StepStatus.SKIPPED
                    continue

                execution.current_step = step_def.step_id
                step_exec = StepExecution(
                    execution_id=execution.execution_id,
                    step_id=step_def.step_id,
                    status=StepStatus.PENDING,
                )

                tasks.append(
                    self._run_step_with_retries(
                        step_def=step_def,
                        execution=execution,
                        actor=actor,
                        step_exec=step_exec,
                    )
                )

            if tasks:
                results = await asyncio.gather(*tasks)
                for step_def, step_exec in zip(level, results, strict=False):
                    step_statuses[step_def.step_id] = step_exec.status
                    if step_exec.output:
                        execution.output_payload.update(step_exec.output)

                    if step_exec.status == StepStatus.WAITING_APPROVAL:
                        execution.transition_to(WorkflowStatus.WAITING_APPROVAL)
                        if self.wf_exec_repo:
                            await self.wf_exec_repo.save(execution)
                        return execution

                    if step_exec.status == StepStatus.FAILED:
                        execution.failure_reason = step_exec.error
                        execution.transition_to(WorkflowStatus.FAILED)
                        execution.completed_at = datetime.now(tz=UTC)
                        if self.wf_exec_repo:
                            await self.wf_exec_repo.save(execution)

                        # Move to DLQ
                        if self.dlq_repo:
                            dlq_item = DeadLetterJob(
                                execution_id=execution.execution_id,
                                workflow_id=workflow_def.workflow_id,
                                organization_id=execution.organization_id,
                                failure_reason=step_exec.error or "Step execution failed",
                                error_category=self.retry_service.classify_error(step_exec.error or ""),
                                payload=execution.input_payload,
                            )
                            await self.dlq_repo.save(dlq_item)

                        return execution

        # All steps completed successfully!
        if execution.status == WorkflowStatus.RUNNING:
            execution.transition_to(WorkflowStatus.COMPLETED)
            execution.completed_at = datetime.now(tz=UTC)
            if self.wf_exec_repo:
                await self.wf_exec_repo.save(execution)

            await self.event_bus.publish(
                Event(
                    event_type="hrms.workflow.completed",
                    source=actor.actor_id,
                    payload={
                        "workflow_id": workflow_def.workflow_id,
                        "execution_id": execution.execution_id,
                        "organization_id": execution.organization_id,
                    },
                    correlation_id=execution.correlation_id,
                )
            )

        return execution

    async def _run_step_with_retries(
        self,
        step_def: WorkflowStepDefinition,
        execution: WorkflowExecution,
        actor: Actor,
        step_exec: StepExecution,
    ) -> StepExecution:
        """Run step execution loop with retry policies and error classification."""
        max_attempts = int(step_def.retry_policy.get("max_attempts", 3))

        for attempt in range(1, max_attempts + 1):
            step_exec.attempt = attempt
            if self.step_exec_repo:
                await self.step_exec_repo.save(step_exec)

            step_exec = await self.step_executor.execute_step(
                step_def=step_def,
                execution=execution,
                actor=actor,
                step_exec=step_exec,
            )

            if step_exec.status in (StepStatus.SUCCEEDED, StepStatus.WAITING_APPROVAL):
                if self.step_exec_repo:
                    await self.step_exec_repo.save(step_exec)
                return step_exec

            # Check if retryable
            is_eligible = self.retry_service.is_retryable(error=step_exec.error or "", attempt=attempt, max_attempts=max_attempts)

            if not is_eligible:
                if self.step_exec_repo:
                    await self.step_exec_repo.save(step_exec)
                return step_exec

            # Next retry backoff timestamp
            next_retry = self.retry_service.calculate_next_retry(attempt, step_def.retry_policy)
            step_exec.next_retry_at = next_retry

        return step_exec
