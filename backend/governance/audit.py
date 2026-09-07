"""
Governance — Audit Event contracts.

Every significant action in the HRMS must generate an immutable AuditEvent.
Audit records must never be deleted or modified after creation.
PII must never appear unmasked in audit records.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AuditAction(StrEnum):
    """Categories of auditable actions."""

    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"

    # Data access
    DATA_READ = "DATA_READ"
    DATA_CREATED = "DATA_CREATED"
    DATA_UPDATED = "DATA_UPDATED"
    DATA_DELETED = "DATA_DELETED"

    # AI / Agent actions
    AGENT_EXECUTED = "AGENT_EXECUTED"
    AI_DECISION_MADE = "AI_DECISION_MADE"
    AI_RECOMMENDATION_GENERATED = "AI_RECOMMENDATION_GENERATED"

    # Governance
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_REJECTED = "APPROVAL_REJECTED"
    APPROVAL_EXPIRED = "APPROVAL_EXPIRED"
    APPROVAL_ESCALATED = "APPROVAL_ESCALATED"

    # Autonomy
    AUTONOMY_LEVEL_CHANGED = "AUTONOMY_LEVEL_CHANGED"
    EMERGENCY_STOP_TRIGGERED = "EMERGENCY_STOP_TRIGGERED"
    EMERGENCY_STOP_CLEARED = "EMERGENCY_STOP_CLEARED"

    # HR actions
    EMPLOYEE_CREATED = "EMPLOYEE_CREATED"
    EMPLOYEE_UPDATED = "EMPLOYEE_UPDATED"
    EMPLOYEE_TERMINATED = "EMPLOYEE_TERMINATED"
    PAYROLL_PROCESSED = "PAYROLL_PROCESSED"
    CANDIDATE_REJECTED = "CANDIDATE_REJECTED"
    POLICY_MODIFIED = "POLICY_MODIFIED"

    # Command
    COMMAND_RECEIVED = "COMMAND_RECEIVED"
    COMMAND_EXECUTED = "COMMAND_EXECUTED"
    COMMAND_FAILED = "COMMAND_FAILED"

    # Security
    PERMISSION_DENIED = "PERMISSION_DENIED"
    PII_ACCESSED = "PII_ACCESSED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class AuditEvent(BaseModel):
    """
    Immutable audit record for a single system action.

    Audit events are append-only and must not contain raw PII.
    """

    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: AuditAction
    actor_id: str = Field(description="ID of the user or agent that performed the action")
    actor_role: str = Field(description="Role of the actor at time of action")
    resource_type: str = Field(description="Type of resource affected, e.g. 'Employee'")
    resource_id: str | None = Field(default=None, description="ID of the affected resource")
    channel: str = Field(description="Interface channel through which the action was performed")
    outcome: str = Field(description="'success' or 'failure'")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional non-PII context for the action",
    )
    ip_address: str | None = Field(default=None)
    correlation_id: str | None = Field(
        default=None,
        description="Links this event to a parent command or workflow",
    )
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    model_config = {"frozen": True}  # Immutable after creation


class AuditTrail(BaseModel):
    """A chronological collection of audit events for a resource or correlation."""

    resource_type: str
    resource_id: str
    events: list[AuditEvent] = Field(default_factory=list)

    @property
    def event_count(self) -> int:
        return len(self.events)

    def filter_by_action(self, action: AuditAction) -> list[AuditEvent]:
        return [e for e in self.events if e.action == action]
