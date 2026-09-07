"""
Agent Planning Models — Plan and PlanStep domain models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.planning.domain.enums import PlanStatus, StepStatus


def generate_plan_id(prefix: str = "plan") -> str:
    """Generate prefixed random UUID for plan entities."""
    return f"{prefix}-{uuid.uuid4()}"


def generate_step_id(prefix: str = "step") -> str:
    """Generate prefixed random UUID for step entities."""
    return f"{prefix}-{uuid.uuid4()}"


class PlanStep(BaseModel):
    """
    Individual executable step within an Agent Plan.
    """

    step_id: str = Field(default_factory=lambda: generate_step_id("step"))
    sequence: int = Field(default=1, description="Execution order sequence")
    description: str = Field(description="Human readable step summary")
    action_type: str = Field(default="TOOL_CALL", description="Action tier e.g. TOOL_CALL, REASON, QUERY")
    tool_name: str = Field(description="Target tool_id e.g. employee.get")
    command_type: str = Field(default="", description="Mapped command_type e.g. employee.read")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Execution arguments payload")
    dependencies: list[str] = Field(default_factory=list, description="Step IDs that must complete first")
    status: StepStatus = Field(default=StepStatus.PENDING)
    retry_count: int = Field(default=0)
    result: dict[str, Any] = Field(default_factory=dict, description="Step execution outcome payload")
    failure_reason: str | None = Field(default=None)
    requires_approval: bool = Field(default=False)
    risk_level: str = Field(default="LOW")


class Plan(BaseModel):
    """
    DAG execution plan created by Reasoning Engine for an AgentTask.
    """

    plan_id: str = Field(default_factory=lambda: generate_plan_id("plan"))
    agent_id: str = Field(description="Target agent ID")
    task_id: str = Field(description="Target agent task ID")
    organization_id: str = Field(description="Tenant isolation boundary")
    status: PlanStatus = Field(default=PlanStatus.DRAFT)
    objective: str = Field(description="Goal or objective being solved")
    steps: list[PlanStep] = Field(default_factory=list, description="DAG plan steps")
    current_step: int = Field(default=0, description="Active step sequence index")
    version: int = Field(default=1, description="Plan revision iteration")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = Field(default=None)
    failure_reason: str | None = Field(default=None)
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4()}")
