"""
Agent Domain — Entities for Agent, AgentCapability, AgentTask, and AgentExecutionContext.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.domain.enums import AgentStatus, AgentType, TaskPriority, TaskStatus
from backend.agents.domain.exceptions import AgentLifecycleError, AgentTaskError


def generate_agent_id(prefix: str = "agent") -> str:
    """Generate prefixed random UUID for agent entities."""
    return f"{prefix}-{uuid.uuid4()}"


class AgentCapability(BaseModel):
    """
    Structured capability declaration for an AI Agent.
    Note: Capabilities are business declarations; Node 4 security permissions remain authoritative.
    """

    capability_id: str = Field(description="Unique capability identifier e.g. cap_employee_read")
    name: str = Field(description="Human readable capability title e.g. Read Employee Directory")
    description: str = Field(default="")
    resource: str = Field(description="Target resource domain e.g. employee, recruitment, payroll")
    actions: list[str] = Field(default_factory=list, description="Allowed actions e.g. ['read', 'create', 'update']")
    risk_level: str = Field(default="MEDIUM", description="Associated risk tier LOW, MEDIUM, HIGH, CRITICAL")
    requires_hitl: bool = Field(default=False)
    enabled: bool = Field(default=True)


class Agent(BaseModel):
    """
    Core AI Agent domain model.
    Tenant-scoped, mapped to an Actor (ActorType.AI_AGENT).
    """

    agent_id: str = Field(default_factory=lambda: generate_agent_id("agent"))
    organization_id: str = Field(description="Tenant ID boundary")
    name: str = Field(description="Unique agent system name e.g. resume-screener-01")
    display_name: str = Field(description="Human friendly display title e.g. Resume Screening Assistant")
    description: str = Field(default="")
    agent_type: AgentType = Field(default=AgentType.CUSTOM_AGENT)
    status: AgentStatus = Field(default=AgentStatus.CREATED)
    actor_id: str = Field(description="Mapped security Actor ID (ActorType.AI_AGENT)")
    version: int = Field(default=1)
    capabilities: list[AgentCapability] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    system_instructions_reference: str | None = Field(default=None)
    max_concurrent_tasks: int = Field(default=5)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    def transition_to(self, new_status: AgentStatus) -> None:
        """Enforce strict lifecycle transitions for Agent."""
        if self.status == new_status:
            return

        allowed: dict[AgentStatus, set[AgentStatus]] = {
            AgentStatus.CREATED: {AgentStatus.ACTIVE, AgentStatus.DISABLED},
            AgentStatus.ACTIVE: {
                AgentStatus.PAUSED,
                AgentStatus.SUSPENDED,
                AgentStatus.DRAINING,
                AgentStatus.DISABLED,
            },
            AgentStatus.PAUSED: {AgentStatus.ACTIVE, AgentStatus.DISABLED},
            AgentStatus.SUSPENDED: {AgentStatus.ACTIVE, AgentStatus.DISABLED},
            AgentStatus.DRAINING: {AgentStatus.DISABLED},
            AgentStatus.DISABLED: {AgentStatus.ACTIVE, AgentStatus.TERMINATED},
            AgentStatus.TERMINATED: set(),
        }

        valid_next = allowed.get(self.status, set())
        if new_status not in valid_next:
            raise AgentLifecycleError(f"Invalid agent status transition from '{self.status.value}' to '{new_status.value}'.")
        self.status = new_status
        self.updated_at = datetime.now(tz=UTC)

    def has_capability(self, resource: str, action: str) -> bool:
        """Check if the agent possesses an enabled capability for resource and action."""
        return any(cap.enabled and cap.resource == resource and action in cap.actions for cap in self.capabilities)


class AgentTask(BaseModel):
    """
    Domain entity representing a unit of work assigned to an AI Agent.
    """

    task_id: str = Field(default_factory=lambda: generate_agent_id("task"))
    organization_id: str = Field(description="Tenant ID boundary")
    agent_id: str = Field(description="Assigned Agent ID")
    parent_task_id: str | None = Field(default=None)
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = Field(description="Task goal description e.g. Screen resume for candidate #102")
    description: str = Field(default="")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    status: TaskStatus = Field(default=TaskStatus.CREATED)
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    failure_reason: str | None = Field(default=None)
    retry_count: int = Field(default=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def transition_to(self, new_status: TaskStatus) -> None:
        """Enforce strict lifecycle transitions for AgentTask."""
        if self.status == new_status:
            return

        allowed: dict[TaskStatus, set[TaskStatus]] = {
            TaskStatus.CREATED: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
            TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
            TaskStatus.RUNNING: {
                TaskStatus.WAITING,
                TaskStatus.WAITING_APPROVAL,
                TaskStatus.DELEGATED,
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            },
            TaskStatus.WAITING: {TaskStatus.RUNNING, TaskStatus.FAILED, TaskStatus.CANCELLED},
            TaskStatus.WAITING_APPROVAL: {TaskStatus.RUNNING, TaskStatus.FAILED, TaskStatus.CANCELLED},
            TaskStatus.DELEGATED: {TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED},
            TaskStatus.COMPLETED: set(),
            TaskStatus.FAILED: set(),
            TaskStatus.CANCELLED: set(),
            TaskStatus.EXPIRED: set(),
        }

        valid_next = allowed.get(self.status, set())
        if new_status not in valid_next:
            raise AgentTaskError(f"Invalid task status transition from '{self.status.value}' to '{new_status.value}'.")
        self.status = new_status


class AgentExecutionContext(BaseModel):
    """
    Immutable execution context token passed to runtime engines.
    Contains agent identity, mapped actor, tenant ID, and capability snapshots.
    """

    agent_id: str
    actor_id: str
    organization_id: str
    task_id: str
    correlation_id: str
    capabilities: list[str] = Field(default_factory=list, description="Resource:action capability tokens")
    metadata: dict[str, Any] = Field(default_factory=dict)
    deadline: datetime | None = Field(default=None)
