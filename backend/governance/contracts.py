"""
Governance — Core governance contracts.

Defines governance policies, decisions, and violation records that control
the behavior of autonomous agents across the entire HRMS platform.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.governance.risk import RiskLevel


class GovernanceScope(StrEnum):
    """Scope at which a governance policy applies."""

    GLOBAL = "GLOBAL"
    ORGANIZATION = "ORGANIZATION"
    DEPARTMENT = "DEPARTMENT"
    AGENT = "AGENT"
    ACTION = "ACTION"
    WORKFLOW = "WORKFLOW"


class GovernancePolicy(BaseModel):
    """
    A governance rule that controls agent autonomy for a specific scope.

    Policies can be stacked — more specific policies override broader ones.
    For example, an AGENT-scoped policy overrides a GLOBAL one.
    """

    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    scope: GovernanceScope
    scope_id: str | None = Field(
        default=None,
        description="ID of the specific scope entity (agent ID, dept ID, etc.)",
    )

    # What this policy governs
    action_types: list[str] = Field(
        default_factory=list,
        description="Action types this policy covers. Empty = applies to all.",
    )

    # Autonomy constraint
    max_autonomy_level: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Maximum autonomy level allowed. 0=human only, 5=fully autonomous.",
    )

    # Risk constraint
    max_risk_without_approval: RiskLevel = Field(
        default=RiskLevel.LOW,
        description="Highest risk level allowed to proceed without approval.",
    )

    # Approval requirements
    requires_approval_from: list[str] = Field(
        default_factory=list,
        description="Roles required to approve actions under this policy.",
    )

    # Rate limiting
    max_actions_per_hour: int | None = Field(default=None)
    max_actions_per_day: int | None = Field(default=None)

    # Lifecycle
    is_active: bool = Field(default=True)
    effective_from: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    effective_until: datetime | None = Field(default=None)
    created_by: str = Field(description="Actor ID who created this policy")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class GovernanceDecision(BaseModel):
    """
    Record of a governance evaluation result for a specific action.

    Created each time the governance layer evaluates whether an agent
    action may proceed, requires approval, or must be blocked.
    """

    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    policy_id: str | None = Field(default=None)
    agent_id: str
    action_type: str
    resource_type: str
    resource_id: str | None = Field(default=None)
    risk_level: RiskLevel
    outcome: str = Field(description="'allow', 'require_approval', or 'block'")
    reason: str
    applied_policy_name: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    model_config = {"frozen": True}


class GovernanceViolation(BaseModel):
    """
    Record of an attempted policy violation by an agent.

    Violations must trigger immediate alerts and be stored permanently.
    Repeated violations may trigger automatic emergency stop.
    """

    violation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    agent_role: str
    action_type: str
    violated_policy_id: str | None = Field(default=None)
    violated_policy_name: str | None = Field(default=None)
    violation_description: str
    severity: RiskLevel
    was_blocked: bool = Field(description="True if the action was prevented")
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    model_config = {"frozen": True}
