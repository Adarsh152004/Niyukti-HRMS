"""
Enterprise Runtime — Task Manager.

Defines contracts for background task scheduling, tracking, and lifecycle management.
Concrete implementations (Celery, asyncio, APScheduler) are provided in later nodes.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class TaskStatus(StrEnum):
    """Lifecycle states of a managed background task."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"


class TaskPriority(StrEnum):
    """Priority levels for task scheduling."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskRecord:
    """
    Immutable record of a managed task.

    Attributes:
        task_id: Unique task identifier.
        name: Human-readable task name.
        status: Current lifecycle status.
        priority: Scheduling priority.
        agent_id: Optional ID of the agent that owns this task.
        created_at: When the task was submitted.
        started_at: When execution began.
        completed_at: When execution ended (success or failure).
        error: Error message if the task failed.
        result: Task output payload (sanitized — no raw PII).
    """

    __slots__ = (
        "agent_id",
        "completed_at",
        "created_at",
        "error",
        "name",
        "priority",
        "result",
        "started_at",
        "status",
        "task_id",
    )

    def __init__(
        self,
        name: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        agent_id: str | None = None,
    ) -> None:
        self.task_id: str = str(uuid.uuid4())
        self.name: str = name
        self.status: TaskStatus = TaskStatus.PENDING
        self.priority: TaskPriority = priority
        self.agent_id: str | None = agent_id
        self.created_at: datetime = datetime.now(tz=UTC)
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.error: str | None = None
        self.result: dict[str, Any] | None = None

    def __repr__(self) -> str:
        return f"TaskRecord(id={self.task_id!r}, name={self.name!r}, status={self.status})"


# Type alias for async task callables
AsyncTaskCallable = Callable[[], Coroutine[Any, Any, dict[str, Any] | None]]


class TaskManager(ABC):
    """
    Abstract task manager interface.

    Manages lifecycle of background tasks: submission, monitoring, cancellation.
    """

    @abstractmethod
    async def submit(
        self,
        name: str,
        coro: AsyncTaskCallable,
        priority: TaskPriority = TaskPriority.NORMAL,
        agent_id: str | None = None,
    ) -> TaskRecord:
        """
        Submit an async task for execution.

        Returns:
            TaskRecord with PENDING status and assigned task_id.
        """
        ...

    @abstractmethod
    async def get(self, task_id: str) -> TaskRecord | None:
        """Retrieve a task record by ID."""
        ...

    @abstractmethod
    async def cancel(self, task_id: str) -> bool:
        """
        Request cancellation of a running task.

        Returns:
            True if the cancellation request was accepted.
        """
        ...

    @abstractmethod
    async def list_tasks(
        self,
        status: TaskStatus | None = None,
        agent_id: str | None = None,
    ) -> list[TaskRecord]:
        """List tasks, optionally filtered by status and/or agent."""
        ...
