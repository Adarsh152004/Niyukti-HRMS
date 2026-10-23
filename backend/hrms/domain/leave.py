"""HRMS Domain — LeaveRequest."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import Field

from backend.hrms.domain.common import (
    HRMSBaseModel,
    LeaveStatus,
    LeaveType,
    generate_id,
    utc_now,
)


class LeaveRequest(HRMSBaseModel):
    """
    An employee leave request.

    Leave requests flow through an approval workflow.
    Manager approval is required for most leave types.
    """

    leave_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    leave_type: LeaveType
    start_date: date
    end_date: date
    total_days: float = Field(ge=0.0)
    is_half_day: bool = Field(default=False)
    half_day_session: str | None = Field(default=None, description="'MORNING' or 'AFTERNOON' for half-day leaves")
    reason: str | None = Field(default=None)
    status: LeaveStatus = Field(default=LeaveStatus.PENDING)

    # Approval
    approved_by: str | None = Field(default=None, description="Manager/HR employee ID")
    approved_at: datetime | None = Field(default=None)
    rejected_by: str | None = Field(default=None)
    rejected_at: datetime | None = Field(default=None)
    rejection_reason: str | None = Field(default=None)
    approval_request_id: str | None = Field(
        default=None,
        description="Links to ApprovalRequest if routed through workflow",
    )

    # Supporting document
    document_key: str | None = Field(default=None, description="Storage key for supporting document (e.g. medical cert)")

    # Cancellation
    cancelled_at: datetime | None = Field(default=None)
    cancelled_by: str | None = Field(default=None)

    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
