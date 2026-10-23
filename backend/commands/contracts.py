"""
Command Architecture — Command and Intent contracts.

A Command is the central object flowing through the HRMS command pipeline.
It carries the actor's intent from any channel through authentication,
authorization, intent parsing, governance, agent execution, and audit.

Pipeline:
    Channel → Authentication → Authorization → CommandParser
    → Intent → Policy/Governance → Agent/Workflow → Execution
    → Validation → HITL (if required) → Result → Audit → Response
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.commands.channels import Channel
from backend.governance.risk import RiskLevel


class ExecutionStatus(StrEnum):
    """Lifecycle status of a command execution."""

    RECEIVED = "RECEIVED"
    AUTHENTICATED = "AUTHENTICATED"
    AUTHORIZED = "AUTHORIZED"
    PARSED = "PARSED"
    VALIDATED = "VALIDATED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class IntentCategory(StrEnum):
    """High-level categories for command intents."""

    # Analytics & Reporting
    ANALYTICS = "ANALYTICS"
    REPORT = "REPORT"

    # Employee Management
    EMPLOYEE_QUERY = "EMPLOYEE_QUERY"
    EMPLOYEE_ACTION = "EMPLOYEE_ACTION"

    # Recruitment
    RECRUITMENT_QUERY = "RECRUITMENT_QUERY"
    RECRUITMENT_ACTION = "RECRUITMENT_ACTION"

    # Attendance & Leave
    ATTENDANCE_QUERY = "ATTENDANCE_QUERY"
    LEAVE_ACTION = "LEAVE_ACTION"

    # Payroll
    PAYROLL_QUERY = "PAYROLL_QUERY"
    PAYROLL_ACTION = "PAYROLL_ACTION"

    # Performance
    PERFORMANCE_QUERY = "PERFORMANCE_QUERY"
    PERFORMANCE_ACTION = "PERFORMANCE_ACTION"

    # Governance / Control
    AUTONOMY_CONTROL = "AUTONOMY_CONTROL"
    APPROVAL_ACTION = "APPROVAL_ACTION"
    POLICY_ACTION = "POLICY_ACTION"
    AUDIT_QUERY = "AUDIT_QUERY"

    # Agent Control
    AGENT_CONTROL = "AGENT_CONTROL"
    AGENT_QUERY = "AGENT_QUERY"

    # Training / Career
    TRAINING_QUERY = "TRAINING_QUERY"
    TRAINING_ACTION = "TRAINING_ACTION"

    # Unknown
    UNKNOWN = "UNKNOWN"


class Intent(BaseModel):
    """
    Parsed intent extracted from a natural-language or structured command.

    Produced by the CommandParser after receiving the raw command text.
    """

    intent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: IntentCategory
    action: str = Field(description="Specific action, e.g. 'list_high_attrition_employees'")
    entities: dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted entities from the command, e.g. {'department': 'Engineering'}",
    )
    raw_text: str | None = Field(default=None, description="Original natural-language text")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class Command(BaseModel):
    """
    The central command object in the HRMS command pipeline.

    Carries all context from receipt through execution and audit.
    Created by a ChannelAdapter and processed by the application layer.

    Example flow::

        CEO → WhatsApp: "Show employees at high attrition risk"
        ↓
        WhatsAppChannelAdapter.receive() → creates Command
        ↓
        CommandPipeline: authenticate → authorize → parse intent
        → governance check → execute → HITL if needed → respond → audit
    """

    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Actor
    actor_id: str = Field(description="Authenticated user or agent ID issuing the command")
    actor_role: str = Field(description="Role of the actor at time of issuance")

    # Channel
    channel: Channel

    # Raw input
    raw_input: str | None = Field(
        default=None,
        description="Raw natural-language or structured input from the channel",
    )

    # Parsed intent (populated after parsing stage)
    intent: Intent | None = Field(default=None)

    # Structured parameters (populated after validation)
    parameters: dict[str, Any] = Field(default_factory=dict)

    # Risk and authorization
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
    requires_approval: bool = Field(default=False)
    approval_request_id: str | None = Field(default=None)
    hitl_request_id: str | None = Field(default=None)

    # Execution
    execution_status: ExecutionStatus = Field(default=ExecutionStatus.RECEIVED)
    assigned_agent_id: str | None = Field(default=None)
    assigned_agent_role: str | None = Field(default=None)

    # Result
    result: dict[str, Any] | None = Field(default=None)
    error: str | None = Field(default=None)

    # Lifecycle timestamps
    correlation_id: str | None = Field(
        default=None,
        description="Links related commands, events, and audit records",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = Field(default=None)


class CommandResult(BaseModel):
    """
    Final result of a command execution, returned to the channel adapter.
    """

    command_id: str
    status: ExecutionStatus
    success: bool
    data: dict[str, Any] | None = Field(default=None)
    message: str | None = Field(default=None)
    error: str | None = Field(default=None)
    hitl_required: bool = Field(default=False)
    hitl_request_id: str | None = Field(default=None)
    audit_event_id: str | None = Field(default=None)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
