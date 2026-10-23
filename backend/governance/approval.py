"""
Governance — Approval Request contracts.

Approval requests are the general mechanism for any action that requires
explicit authorization. Unlike HITL (which is agent→human), approvals can
flow between any actors in the system.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.governance.risk import RiskLevel


class ApprovalStatus(StrEnum):
    """Lifecycle states of an approval request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ESCALATED = "ESCALATED"
    CANCELLED = "CANCELLED"

    @property
    def is_terminal(self) -> bool:
        return self in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.EXPIRED,
            ApprovalStatus.CANCELLED,
        )


class ApprovalRequest(BaseModel):
    """
    A formal request for authorization of a significant system action.

    Approval requests are created for:
    - High-risk autonomous agent actions
    - Workflow transitions requiring sign-off
    - Policy changes
    - Payroll modifications
    - Employee terminations
    """

    approval_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    action_description: str
    requester_id: str = Field(description="User or agent ID requesting the action")
    requester_role: str

    risk_level: RiskLevel
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)

    resource_type: str
    resource_id: str | None = Field(default=None)
    parameters: dict[str, Any] = Field(default_factory=dict)

    # Approver requirements
    required_approver_role: str
    assigned_approver_id: str | None = Field(default=None)

    # Decision fields
    approver_id: str | None = Field(default=None)
    approval_reason: str | None = Field(default=None)
    rejection_reason: str | None = Field(default=None)
    evidence: list[str] = Field(default_factory=list)

    # Escalation
    escalation_target_role: str | None = Field(default=None)
    escalated_at: datetime | None = Field(default=None)
    escalation_reason: str | None = Field(default=None)

    # Lifecycle
    expires_at: datetime | None = Field(default=None)
    correlation_id: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    decided_at: datetime | None = Field(default=None)


class ApprovalRecord(BaseModel):
    """
    Immutable final record of an approval decision.

    Stored permanently in the audit trail.
    """

    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    approval_id: str
    final_status: ApprovalStatus
    approver_id: str
    approver_role: str
    reason: str | None = Field(default=None)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    model_config = {"frozen": True}
