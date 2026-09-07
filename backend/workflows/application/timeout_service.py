"""
Timeout Service — Step Execution Timeout Evaluator.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from backend.workflows.domain.models import StepExecution


class TimeoutService:
    """
    Evaluates step execution timeout status.
    """

    @staticmethod
    def is_timed_out(step_exec: StepExecution, timeout_seconds: int) -> bool:
        """Check if a running step execution has exceeded allowed timeout limit."""
        if not step_exec.started_at or step_exec.completed_at:
            return False

        now = datetime.now(tz=UTC)
        deadline = step_exec.started_at + timedelta(seconds=timeout_seconds)
        return now > deadline
