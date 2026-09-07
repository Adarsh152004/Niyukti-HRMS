"""HRMS Domain — Notification."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from backend.hrms.domain.common import (
    HRMSBaseModel,
    NotificationChannel,
    NotificationStatus,
    generate_id,
    utc_now,
)


class Notification(HRMSBaseModel):
    """
    A notification sent to an employee or actor.

    Notifications are dispatched by the Notification Agent.
    PII must not appear in notification metadata or logs.
    """

    notification_id: str = Field(default_factory=generate_id)
    organization_id: str
    recipient_id: str = Field(description="Employee/user ID of the recipient")
    channel: NotificationChannel
    title: str
    body: str
    notification_type: str = Field(description="e.g. 'leave_approved', 'payslip_ready', 'approval_required'")
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)
    priority: str = Field(default="NORMAL", description="LOW, NORMAL, HIGH, URGENT")
    reference_type: str | None = Field(default=None, description="Type of linked resource, e.g. 'LeaveRequest'")
    reference_id: str | None = Field(default=None, description="ID of linked resource")
    action_url: str | None = Field(default=None, description="Deep link for web/app")
    metadata: dict[str, Any] = Field(default_factory=dict)
    sent_at: datetime | None = Field(default=None)
    delivered_at: datetime | None = Field(default=None)
    read_at: datetime | None = Field(default=None)
    error_message: str | None = Field(default=None)
    retry_count: int = Field(default=0, ge=0)
    scheduled_for: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
