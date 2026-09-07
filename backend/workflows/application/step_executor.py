"""
Step Executor — Executes Workflow Steps via Node 5 CommandBus.

CRITICAL INVARIANT:
Workflow steps MUST execute through Node 5 CommandBus (`CommandBus.dispatch()`).
No direct database or repository mutation calls are permitted!
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.commands.application.bus import CommandBus, CommandBusExecutionError
from backend.commands.domain.enums import CommandChannel, CommandStatus
from backend.commands.domain.models import Command
from backend.hrms.domain.actor import Actor
from backend.workflows.domain.enums import StepStatus
from backend.workflows.domain.models import StepExecution, WorkflowExecution, WorkflowStepDefinition


class StepExecutor:
    """
    Executes an individual Workflow Step by submitting a Command to CommandBus.
    """

    def __init__(self, command_bus: CommandBus | None = None) -> None:
        self.command_bus = command_bus or CommandBus()

    async def execute_step(
        self,
        step_def: WorkflowStepDefinition,
        execution: WorkflowExecution,
        actor: Actor,
        step_exec: StepExecution,
    ) -> StepExecution:
        """
        Execute step by dispatching Command through Node 5 CommandBus pipeline.
        """
        now = datetime.now(tz=UTC)
        step_exec.status = StepStatus.RUNNING
        step_exec.started_at = now

        # Merge input payload with step definition payload template
        merged_payload = {**execution.input_payload, **step_def.command_payload}

        cmd = Command(
            command_type=step_def.command_type,
            actor_id=actor.actor_id,
            organization_id=actor.organization_id,
            channel=CommandChannel.AGENT if actor.is_ai_agent else CommandChannel.WEB,
            payload=merged_payload,
            idempotency_key=f"{execution.workflow_id}-{execution.execution_id}-{step_def.step_id}-{step_exec.attempt}",
        )

        # Check if this step was waiting for approval and has now been approved
        for req in self.command_bus.approval_service._requests_by_id.values():
            if (
                req.organization_id == actor.organization_id
                and req.status.value == "APPROVED"
                and req.target_action == step_def.command_type
            ):
                cmd.status = CommandStatus.APPROVED
                break

        context = self.command_bus.build_context(
            actor=actor,
            channel=CommandChannel.AGENT if actor.is_ai_agent else CommandChannel.WEB,
        )

        try:
            res = await self.command_bus.dispatch(cmd, context)

            if res.status == CommandStatus.WAITING_APPROVAL:
                step_exec.status = StepStatus.WAITING_APPROVAL
                step_exec.output = res.result_data
                return step_exec

            if res.status == CommandStatus.SUCCEEDED:
                step_exec.status = StepStatus.SUCCEEDED
                step_exec.completed_at = datetime.now(tz=UTC)
                step_exec.output = res.result_data
                return step_exec

            step_exec.status = StepStatus.FAILED
            step_exec.error = f"Command execution ended in status '{res.status.value}'"
            return step_exec

        except CommandBusExecutionError as e:
            step_exec.status = StepStatus.FAILED
            step_exec.error = f"CommandBus execution error: {e.message}"
            return step_exec
        except Exception as e:
            step_exec.status = StepStatus.FAILED
            step_exec.error = str(e)
            return step_exec
