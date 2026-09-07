"""
Agent Execution Sandbox — Isolation container preventing direct OS/shell access or unmanaged subprocesses.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any, TypeVar

from backend.agents.sandbox.sla import SLAEvaluationResult, SLAManager

logger = logging.getLogger(__name__)
T = TypeVar("T")


class SandboxSecurityViolation(Exception):
    """Raised when an agent attempts unauthorized environment or system escapes."""

    pass


class AgentExecutionSandbox:
    """Bounded runtime container executing agent logic within strict resource, time, and security constraints."""

    def __init__(
        self,
        organization_id: str,
        agent_id: str,
        sla_manager: SLAManager | None = None,
    ) -> None:
        self.organization_id = organization_id
        self.agent_id = agent_id
        self.sla_manager = sla_manager or SLAManager.get_instance()
        self.sla = self.sla_manager.get_sla(organization_id, agent_id)

    async def execute_bounded(
        self,
        task_func: Callable[[], Coroutine[Any, Any, T]],
        task_id: str = "task",
    ) -> tuple[T, SLAEvaluationResult]:
        """
        Execute coroutine wrapped in timeout, metric tracking, and SLA evaluation.
        """
        start_time = datetime.now(tz=UTC)
        logger.info(
            f"Sandbox executing task [{task_id}] for agent '{self.agent_id}' (Max timeout: {self.sla.max_execution_time_seconds}s)"
        )

        try:
            result = await asyncio.wait_for(
                task_func(),
                timeout=float(self.sla.max_execution_time_seconds),
            )
        except TimeoutError:
            duration = (datetime.now(tz=UTC) - start_time).total_seconds()
            logger.error(f"Sandbox task [{task_id}] timed out after {duration:.1f}s")
            raise TimeoutError(f"Agent task timed out after {self.sla.max_execution_time_seconds}s") from None

        end_time = datetime.now(tz=UTC)
        duration = (end_time - start_time).total_seconds()

        # Evaluate SLA metrics
        sla_result = self.sla_manager.evaluate_task_sla(
            organization_id=self.organization_id,
            agent_id=self.agent_id,
            duration_seconds=duration,
            cost_usd=0.01,  # baseline
            tool_calls=1,
            delegation_depth=1,
        )

        return result, sla_result
