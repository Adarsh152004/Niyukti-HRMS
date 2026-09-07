"""
TaskManager — Coordinates AgentTask state transitions during autonomous orchestration.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.agents.application.task_service import AgentTaskService
from backend.agents.domain.enums import TaskStatus
from backend.agents.domain.models import AgentTask

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages task lifecycle transitions for agent tasks.
    """

    def __init__(self, task_service: AgentTaskService | None = None) -> None:
        self.task_service = task_service or AgentTaskService()

    async def start_task(self, organization_id: str, task_id: str) -> AgentTask:
        """Move task to IN_PROGRESS."""
        return await self.task_service.start_task(organization_id, task_id)

    async def complete_task(
        self,
        organization_id: str,
        task_id: str,
        result: dict[str, Any] | None = None,
    ) -> AgentTask:
        """Move task to COMPLETED."""
        return await self.task_service.complete_task(organization_id, task_id, output=result or {})

    async def fail_task(
        self,
        organization_id: str,
        task_id: str,
        reason: str,
    ) -> AgentTask:
        """Move task to FAILED."""
        return await self.task_service.fail_task(organization_id, task_id, reason=reason)

    async def pause_task(
        self,
        organization_id: str,
        task_id: str,
    ) -> AgentTask:
        """Pause task execution."""
        task = await self.task_service.get_task(organization_id, task_id)
        if task:
            task.transition_to(TaskStatus.WAITING_APPROVAL)
            await self.task_service.repository.save(task)
            return task
        raise ValueError(f"Task '{task_id}' not found.")

    async def resume_task(
        self,
        organization_id: str,
        task_id: str,
    ) -> AgentTask:
        """Resume task execution."""
        task = await self.task_service.get_task(organization_id, task_id)
        if task:
            task.transition_to(TaskStatus.RUNNING)
            await self.task_service.repository.save(task)
            return task
        raise ValueError(f"Task '{task_id}' not found.")

    async def cancel_task(
        self,
        organization_id: str,
        task_id: str,
    ) -> AgentTask:
        """Cancel task execution."""
        task = await self.task_service.get_task(organization_id, task_id)
        if task:
            task.transition_to(TaskStatus.CANCELLED)
            await self.task_service.repository.save(task)
            return task
        raise ValueError(f"Task '{task_id}' not found.")
