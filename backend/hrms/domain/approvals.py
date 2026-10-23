"""
HRMS Domain — ApprovalRequest, ApprovalDecision, ApprovalPolicy.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, generate_id, utc_now


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ApprovalType(StrEnum):
    LEAVE_APPLICATION = "LEAVE_APPLICATION"
    ATTENDANCE_REGULARIZATION = "ATTENDANCE_REGULARIZATION"
    SALARY_REVISION = "SALARY_REVISION"
    PAYROLL_EXECUTION = "PAYROLL_EXECUTION"
    PROMOTION_REQUEST = "PROMOTION_REQUEST"
    JOB_REQUISITION = "JOB_REQUISITION"
    TERMINATION_PROPOSAL = "TERMINATION_PROPOSAL"
    POLICY_CHANGE = "POLICY_CHANGE"


class ApprovalDecision(HRMSBaseModel):
    """An individual approver's decision on a pending request."""

    decision_id: str = Field(default_factory=generate_id)
    approver_id: str
    approver_role: str
    decision: str = Field(description="'APPROVED' or 'REJECTED'")
    rejection_reason: str | None = None
    modification_payload: dict[str, Any] | None = None
    decided_at: datetime = Field(default_factory=utc_now)


class ApprovalRequest(HRMSBaseModel):
    """Universal Human-In-The-Loop (HITL) approval record for all HRMS domains."""

    approval_id: str = Field(default_factory=generate_id)
    organization_id: str
    approval_type: ApprovalType
    requester_id: str
    requester_role: str
    target_entity_id: str = Field(description="ID of leave, salary, requisition, or employee record")
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    risk_level: str = "MEDIUM"
    payload: dict[str, Any] = Field(default_factory=dict)
    assigned_approvers: list[str] = Field(default_factory=list, description="Actor or Role IDs allowed to decide")
    decisions: list[ApprovalDecision] = Field(default_factory=list)
    sla_deadline: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
