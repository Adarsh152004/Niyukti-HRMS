"""
Agent Task Service — Manages Task creation, queuing, status transitions, and progress tracking.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from backend.agents.domain.enums import TaskPriority, TaskStatus
from backend.agents.domain.events import AgentTaskCreated, AgentTaskFailed, AgentTaskStarted
from backend.agents.domain.exceptions import AgentTaskError
from backend.agents.domain.models import AgentTask
from backend.agents.infrastructure.database.repositories import InMemoryAgentTaskRepository
from backend.agents.ports.repositories import AgentTaskRepositoryPort
from backend.runtime.events import EventBus


class AgentTaskService:
    """
    Manages creation, execution, and lifecycle of AgentTasks.
    """

    def __init__(
        self,
        repository: AgentTaskRepositoryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository = repository or InMemoryAgentTaskRepository()
        self.event_bus = event_bus or EventBus.get_instance()

    async def create_task(
        self,
        organization_id: str,
        agent_id: str,
        goal: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        input_payload: dict[str, Any] | None = None,
        parent_task_id: str | None = None,
    ) -> AgentTask:
        """Create a new AgentTask for an active agent."""
        task = AgentTask(
            organization_id=organization_id,
            agent_id=agent_id,
            goal=goal,
            description=description,
            priority=priority,
            status=TaskStatus.CREATED,
            input=input_payload or {},
            parent_task_id=parent_task_id,
        )

        task.transition_to(TaskStatus.QUEUED)
        saved = await self.repository.save(task)

        await self.event_bus.publish(
            AgentTaskCreated(
                organization_id=organization_id,
                aggregate_id=saved.task_id,
                actor={"actor_id": agent_id, "actor_type": "AI_AGENT"},
                metadata={"goal": goal, "priority": priority.value},
            )
        )
        return saved

    async def start_task(self, organization_id: str, task_id: str) -> AgentTask:
        task = await self.repository.get_by_id(organization_id, task_id)
        if not task:
            raise AgentTaskError(f"Task '{task_id}' not found.")
        task.transition_to(TaskStatus.RUNNING)
        task.started_at = datetime.now(tz=UTC)
        saved = await self.repository.save(task)
        await self.event_bus.publish(
            AgentTaskStarted(
                organization_id=organization_id,
                aggregate_id=task.task_id,
                actor={"actor_id": task.agent_id, "actor_type": "AI_AGENT"},
                metadata={"status": task.status.value},
            )
        )
        return saved

    async def complete_task(self, organization_id: str, task_id: str, output: dict[str, Any]) -> AgentTask:
        task = await self.repository.get_by_id(organization_id, task_id)
        if not task:
            raise AgentTaskError(f"Task '{task_id}' not found.")
        task.transition_to(TaskStatus.COMPLETED)
        task.completed_at = datetime.now(tz=UTC)
        task.output = output
        return await self.repository.save(task)

    async def fail_task(self, organization_id: str, task_id: str, reason: str) -> AgentTask:
        task = await self.repository.get_by_id(organization_id, task_id)
        if not task:
            raise AgentTaskError(f"Task '{task_id}' not found.")
        task.transition_to(TaskStatus.FAILED)
        task.failure_reason = reason
        task.completed_at = datetime.now(tz=UTC)
        saved = await self.repository.save(task)
        await self.event_bus.publish(
            AgentTaskFailed(
                organization_id=organization_id,
                aggregate_id=task.task_id,
                actor={"actor_id": task.agent_id, "actor_type": "AI_AGENT"},
                metadata={"reason": reason},
            )
        )
        return saved

    async def get_task(self, organization_id: str, task_id: str) -> AgentTask | None:
        return await self.repository.get_by_id(organization_id, task_id)

    async def list_tasks_for_agent(self, organization_id: str, agent_id: str) -> Sequence[AgentTask]:
        return await self.repository.list_by_agent(organization_id, agent_id)
