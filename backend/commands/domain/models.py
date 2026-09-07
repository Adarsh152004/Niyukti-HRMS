"""
Command Domain — Core entities for Commands, Metadata, Context, Results, Policy, Risk, Actions, and Idempotency.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.commands.domain.enums import CommandChannel, CommandStatus, PolicyDecision, RiskLevel
from backend.hrms.domain.actor import Actor, ActorType


def generate_cmd_id(prefix: str = "cmd") -> str:
    """Generate a prefixed UUID for command entities."""
    return f"{prefix}-{uuid.uuid4()}"


def calculate_payload_hash(payload: dict[str, Any]) -> str:
    """Calculate deterministic SHA-256 hash of a payload dictionary."""
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class Command(BaseModel):
    """
    Universal Command entity representing an intent to mutate or perform an action.
    """

    command_id: str = Field(default_factory=lambda: generate_cmd_id("cmd"))
    command_type: str = Field(description="Command classifier e.g. employee.create")
    actor_id: str = Field(description="Populated strictly from authenticated security context")
    organization_id: str = Field(description="Tenant boundary")
    channel: CommandChannel = Field(default=CommandChannel.WEB)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: CommandStatus = Field(default=CommandStatus.RECEIVED)
    idempotency_key: str | None = Field(default=None)
    payload_hash: str = Field(default="")

    def model_post_init(self, __context: Any) -> None:
        if not self.payload_hash:
            self.payload_hash = calculate_payload_hash(self.payload)

    def transition_to(self, new_status: CommandStatus) -> None:
        """
        Validate and enforce state transitions according to command lifecycle.
        """
        allowed: dict[CommandStatus, set[CommandStatus]] = {
            CommandStatus.RECEIVED: {CommandStatus.VALIDATING, CommandStatus.CANCELLED},
            CommandStatus.VALIDATING: {CommandStatus.AUTHORIZED, CommandStatus.DENIED, CommandStatus.FAILED},
            CommandStatus.AUTHORIZED: {CommandStatus.POLICY_CHECKED, CommandStatus.DENIED, CommandStatus.FAILED},
            CommandStatus.POLICY_CHECKED: {
                CommandStatus.EXECUTING,
                CommandStatus.WAITING_APPROVAL,
                CommandStatus.DENIED,
                CommandStatus.FAILED,
            },
            CommandStatus.WAITING_APPROVAL: {
                CommandStatus.APPROVED,
                CommandStatus.DENIED,
                CommandStatus.EXPIRED,
                CommandStatus.CANCELLED,
            },
            CommandStatus.APPROVED: {CommandStatus.EXECUTING, CommandStatus.CANCELLED},
            CommandStatus.EXECUTING: {CommandStatus.SUCCEEDED, CommandStatus.FAILED},
            CommandStatus.SUCCEEDED: set(),
            CommandStatus.FAILED: set(),
            CommandStatus.DENIED: set(),
            CommandStatus.CANCELLED: set(),
            CommandStatus.EXPIRED: set(),
        }

        valid_next = allowed.get(self.status, set())
        if new_status not in valid_next:
            raise ValueError(f"Invalid command status transition from '{self.status.value}' to '{new_status.value}'.")
        self.status = new_status


class CommandContext(BaseModel):
    """
    Trusted execution context constructed strictly from security tokens and tenant context.
    Values in this context can NEVER be overridden by payload values.
    """

    actor: Actor
    organization_id: str
    tenant_id: str
    channel: CommandChannel
    permissions: set[str] = Field(default_factory=set)
    capabilities: set[str] = Field(default_factory=set)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str | None = Field(default=None)
    agent_id: str | None = Field(default=None)


class CommandMetadata(BaseModel):
    """
    Metadata schema describing a registered Command type for discovery & AI tool registries.
    """

    command_type: str
    description: str
    required_permissions: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    allowed_actor_types: list[ActorType] = Field(default_factory=lambda: [ActorType.HUMAN, ActorType.AI_AGENT, ActorType.SYSTEM])
    allowed_channels: list[CommandChannel] = Field(
        default_factory=lambda: [
            CommandChannel.WEB,
            CommandChannel.CLI,
            CommandChannel.API,
            CommandChannel.AGENT,
            CommandChannel.SYSTEM,
        ]
    )
    requires_approval: bool = Field(default=False)


class CommandResult(BaseModel):
    """
    Standardized result returned after command execution.
    """

    command_id: str
    status: CommandStatus
    result_data: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = Field(default=None)
    execution_time_ms: float = Field(default=0.0)
    events_produced: list[str] = Field(default_factory=list)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class PolicyContext(BaseModel):
    """Context container provided to Policy Engine rules."""

    command: Command
    context: CommandContext
    resource_data: Any | None = Field(default=None)


class PolicyRule(BaseModel):
    """Individual Policy Engine rule."""

    rule_id: str
    name: str
    description: str
    decision_if_matched: PolicyDecision = Field(default=PolicyDecision.DENY)
    reason: str = Field(default="Policy rule violation")


class PolicyDecisionResult(BaseModel):
    """Outcome of Policy Engine evaluation."""

    decision: PolicyDecision
    rule_id: str | None = Field(default=None)
    reason: str = Field(default="Policy evaluation completed")


class RiskAssessment(BaseModel):
    """Outcome of Risk Engine evaluation."""

    risk_level: RiskLevel
    score: int
    reasons: list[str] = Field(default_factory=list)


class Action(BaseModel):
    """
    Executable action representation produced from a Command.
    """

    action_id: str = Field(default_factory=lambda: generate_cmd_id("act"))
    action_type: str
    command_id: str
    target_resource_type: str
    target_resource_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class IdempotencyRecord(BaseModel):
    """Record storing execution status and result for idempotency deduplication."""

    idempotency_key: str
    command_id: str
    organization_id: str
    payload_hash: str
    status: CommandStatus
    result_data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
