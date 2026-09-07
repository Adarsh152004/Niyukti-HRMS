"""
Workflow Ports — Scheduler & Job Queue Abstract Interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from backend.workflows.domain.models import ScheduledJob


class SchedulerPort(ABC):
    """Abstract interface for background job scheduling (CRON, DELAY, AT_TIME)."""

    @abstractmethod
    async def schedule_job(
        self,
        organization_id: str,
        workflow_id: str,
        execution_id: str,
        scheduled_at: datetime,
        payload: dict[str, Any] | None = None,
    ) -> ScheduledJob:
        pass

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        pass


class JobQueuePort(ABC):
    """Abstract interface for durable job queue operations."""

    @abstractmethod
    async def enqueue(self, job: ScheduledJob) -> ScheduledJob:
        pass

    @abstractmethod
    async def dequeue(self, worker_id: str) -> ScheduledJob | None:
        pass

    @abstractmethod
    async def ack(self, job_id: str) -> None:
        pass

    @abstractmethod
    async def nack(self, job_id: str, error_message: str) -> None:
        pass
