"""HRMS Domain — HRPolicy."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, generate_id, utc_now


class PolicyStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class PolicyCategory(StrEnum):
    LEAVE = "LEAVE"
    ATTENDANCE = "ATTENDANCE"
    PAYROLL = "PAYROLL"
    RECRUITMENT = "RECRUITMENT"
    PERFORMANCE = "PERFORMANCE"
    CODE_OF_CONDUCT = "CODE_OF_CONDUCT"
    TRAINING = "TRAINING"
    IT_SECURITY = "IT_SECURITY"
    DATA_PRIVACY = "DATA_PRIVACY"
    HEALTH_SAFETY = "HEALTH_SAFETY"
    COMPENSATION = "COMPENSATION"
    TRAVEL = "TRAVEL"
    REMOTE_WORK = "REMOTE_WORK"
    OTHER = "OTHER"


class HRPolicy(HRMSBaseModel):
    """
    An organizational HR policy document.

    Policy changes are CRITICAL-risk actions — require CEO/HR_ADMIN approval.
    The Policy Agent enforces active policies during governance checks.
    """

    policy_id: str = Field(default_factory=generate_id)
    organization_id: str
    title: str
    policy_number: str | None = Field(default=None, description="e.g. 'HR-POL-007'")
    category: PolicyCategory
    description: str | None = Field(default=None)
    content: str = Field(description="Full policy text (may be markdown)")
    version: str = Field(default="1.0")
    status: PolicyStatus = Field(default=PolicyStatus.DRAFT)
    applicable_to: list[str] = Field(
        default_factory=list,
        description="Department IDs or ['ALL']",
    )
    effective_date: date | None = Field(default=None)
    review_date: date | None = Field(default=None)
    supersedes_policy_id: str | None = Field(default=None, description="Policy ID this version replaces")
    created_by: str = Field(default="system", description="HR actor who created this policy")
    approved_by: str | None = Field(default=None)
    approval_request_id: str | None = Field(
        default=None,
        description="Approval request — policy changes require CEO/HR_ADMIN approval",
    )
    published_at: datetime | None = Field(default=None)
    document_key: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
