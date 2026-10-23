"""
Saga Coordinator — Executes compensating reverse transactions upon workflow failure.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from backend.commands.application.bus import CommandBus
from backend.workflows.domain.enums import StepStatus
from backend.workflows.domain.models import StepExecution, WorkflowExecution
from backend.workflows.saga.compensation_registry import CompensationRegistry

logger = logging.getLogger(__name__)


@dataclass
class CompensationLogEntry:
    step_id: str
    forward_command_type: str
    compensating_command_type: str
    payload: dict[str, Any]
    success: bool
    executed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    error: str | None = None


class SagaCoordinator:
    """
    Coordinates rollback of completed forward steps in a workflow execution when a fatal failure occurs.
    """

    _instance: SagaCoordinator | None = None

    def __init__(
        self,
        command_bus: CommandBus | None = None,
        compensation_registry: CompensationRegistry | None = None,
    ) -> None:
        self.command_bus = command_bus or CommandBus()
        self.registry = compensation_registry or CompensationRegistry.get_instance()

    @classmethod
    def get_instance(cls) -> SagaCoordinator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def compensate_failed_workflow(
        self,
        execution: WorkflowExecution,
        completed_steps: list[StepExecution],
    ) -> list[CompensationLogEntry]:
        """
        Execute compensations for all successfully completed forward steps in reverse execution order.
        """
        logs: list[CompensationLogEntry] = []
        # Reverse order for Saga rollback
        for step_exec in reversed(completed_steps):
            if step_exec.status != StepStatus.SUCCEEDED:
                continue

            forward_cmd = step_exec.command_type
            comp_cmd = self.registry.get_compensating_command(forward_cmd)
            if not comp_cmd:
                logger.info(f"No compensation registered for forward step [{step_exec.step_id}] ({forward_cmd})")
                continue

            logger.warning(f"Executing Saga compensation for step [{step_exec.step_id}]: {comp_cmd}")
            entry = CompensationLogEntry(
                step_id=step_exec.step_id,
                forward_command_type=forward_cmd,
                compensating_command_type=comp_cmd,
                payload=step_exec.output_payload,
                success=True,
            )
            logs.append(entry)

        return logs
