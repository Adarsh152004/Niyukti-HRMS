"""
Orchestration Models — AgentExecution and AgentExecutionEvent domain entities.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.orchestration.domain.enums import ExecutionState, OrchestrationEventType


def generate_execution_id(prefix: str = "exec") -> str:
    """Generate prefixed random UUID for execution entities."""
    return f"{prefix}-{uuid.uuid4()}"


class AgentExecutionEvent(BaseModel):
    """Event entry recorded during agent orchestration trajectory."""

    event_id: str = Field(default_factory=lambda: f"evt-{uuid.uuid4()}")
    execution_id: str
    organization_id: str
    agent_id: str
    task_id: str
    event_type: OrchestrationEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    payload: dict[str, Any] = Field(default_factory=dict)


class AgentExecution(BaseModel):
    """
    Durable execution trajectory model tracking an AgentTask's autonomous lifecycle.
    """

    execution_id: str = Field(default_factory=lambda: generate_execution_id("exec"))
    organization_id: str = Field(description="Tenant isolation boundary")
    agent_id: str = Field(description="Agent ID")
    task_id: str = Field(description="AgentTask ID")
    plan_id: str | None = Field(default=None, description="Active Plan ID")
    state: ExecutionState = Field(default=ExecutionState.IDLE)
    iteration_count: int = Field(default=0)
    tool_call_count: int = Field(default=0)
    retry_count: int = Field(default=0)
    start_time: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = Field(default=None)
    failure_reason: str | None = Field(default=None)
    result_data: dict[str, Any] = Field(default_factory=dict)
    events: list[AgentExecutionEvent] = Field(default_factory=list)
