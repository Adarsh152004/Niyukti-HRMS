"""
Governance — Human-in-the-Loop (HITL) contracts.

HITL ensures that autonomous agents never silently execute governed actions.
Any action with risk >= HIGH or requiring explicit approval must pause and
create a HITLRequest before proceeding.

States:
    PENDING   → Awaiting human reviewer decision
    APPROVED  → Human approved; agent may proceed
    REJECTED  → Human rejected; agent must not proceed
    EXPIRED   → Approval window elapsed; must escalate or cancel
    ESCALATED → Forwarded to higher authority
    CANCELLED → Withdrawn before decision was made
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.governance.risk import RiskLevel


class HITLStatus(StrEnum):
    """Lifecycle states of a Human-in-the-Loop approval request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ESCALATED = "ESCALATED"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal(self) -> bool:
        """Return True if the status represents a final (non-changeable) state."""
        return self in (
            HITLStatus.APPROVED,
            HITLStatus.REJECTED,
            HITLStatus.EXPIRED,
            HITLStatus.CANCELLED,
        )


class HITLPriority(StrEnum):
    """Priority levels for routing HITL requests to reviewers."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class HITLRequest(BaseModel):
    """
    A formal human approval request raised before a governed action executes.

    The requesting agent MUST NOT proceed until this request reaches
    APPROVED status. If it reaches any other terminal status, the action
    must be aborted and the outcome audited.
    """

    hitl_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = Field(description="The action requiring approval, e.g. 'candidate_rejection'")
    action_description: str = Field(description="Human-readable description of what will happen")
    requesting_agent_id: str = Field(description="ID of the agent raising the request")
    requesting_agent_role: str = Field(description="Role/type of the requesting agent")

    # Risk and priority
    risk_level: RiskLevel
    priority: HITLPriority = Field(default=HITLPriority.NORMAL)

    # Context
    resource_type: str = Field(description="Affected resource type, e.g. 'Candidate'")
    resource_id: str | None = Field(default=None)
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Sanitized (non-PII) parameters of the proposed action",
    )

    # AI recommendation context
    ai_recommendation: str | None = Field(
        default=None,
        description="Summary of the AI recommendation driving this action",
    )
    ai_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    ai_evidence: list[str] = Field(default_factory=list)

    # Reviewer assignment
    required_reviewer_role: str = Field(description="Minimum role required to approve, e.g. 'HR_MANAGER'")
    assigned_reviewer_id: str | None = Field(default=None)

    # Escalation
    escalation_target_role: str | None = Field(
        default=None,
        description="Role to escalate to if approval times out",
    )

    # Lifecycle
    status: HITLStatus = Field(default=HITLStatus.PENDING)
    expires_at: datetime | None = Field(default=None)
    correlation_id: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class HITLDecision(BaseModel):
    """
    Record of a human reviewer's decision on a HITL request.

    Human decisions always override AI recommendations.
    This record is immutable and must be stored permanently.
    """

    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hitl_id: str = Field(description="The HITL request this decision resolves")
    reviewer_id: str
    reviewer_role: str
    decision: HITLStatus = Field(description="The final status applied (APPROVED/REJECTED/etc.)")
    approval_reason: str | None = Field(default=None)
    rejection_reason: str | None = Field(default=None)
    override_ai_recommendation: bool = Field(
        default=False,
        description="True if the human decision contradicts the AI recommendation",
    )
    decided_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    model_config = {"frozen": True}
