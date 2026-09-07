"""
Delegation Domain Models — Entities for Delegation, DelegationGrant, and DelegatedTask.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.delegation.domain.enums import DelegationScope, DelegationStatus
from backend.agents.delegation.domain.exceptions import DelegationValidationError
from backend.agents.domain.models import AgentCapability


def generate_delegation_id(prefix: str = "del") -> str:
    """Generate prefixed random UUID for delegation entities."""
    return f"{prefix}-{uuid.uuid4()}"


class DelegationGrant(BaseModel):
    """
    Immutable grant of capabilities granted from delegator to delegate.
    """

    grant_id: str = Field(default_factory=lambda: generate_delegation_id("grant"))
    delegator_agent_id: str
    delegate_agent_id: str
    granted_capabilities: list[AgentCapability] = Field(default_factory=list)
    scope: DelegationScope = Field(default=DelegationScope.TASK_SCOPED)
    requires_hitl_approval: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class Delegation(BaseModel):
    """
    Core Agent Delegation entity representing bounded capability delegation between AI agents.
    """

    delegation_id: str = Field(default_factory=lambda: generate_delegation_id("del"))
    organization_id: str = Field(description="Tenant isolation boundary")
    delegator_agent_id: str
    delegate_agent_id: str
    parent_task_id: str
    delegated_task_id: str | None = Field(default=None)
    capabilities: list[AgentCapability] = Field(default_factory=list)
    scope: DelegationScope = Field(default=DelegationScope.TASK_SCOPED)
    status: DelegationStatus = Field(default=DelegationStatus.REQUESTED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    expires_at: datetime
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4()}")
    parent_delegation_id: str | None = Field(default=None)
    allow_further_delegation: bool = Field(default=False)
    payload_hash: str | None = Field(default=None)
    rejection_reason: str | None = Field(default=None)
    revocation_reason: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def is_active(self) -> bool:
        """Check if delegation is currently ACTIVE and not expired."""
        if self.status != DelegationStatus.ACTIVE:
            return False
        return datetime.now(tz=UTC) < self.expires_at

    def transition_to(self, new_status: DelegationStatus) -> None:
        """Enforce strict delegation status transitions."""
        if self.status == new_status:
            return

        allowed: dict[DelegationStatus, set[DelegationStatus]] = {
            DelegationStatus.REQUESTED: {
                DelegationStatus.APPROVED,
                DelegationStatus.ACTIVE,
                DelegationStatus.REJECTED,
                DelegationStatus.CANCELLED,
            },
            DelegationStatus.APPROVED: {
                DelegationStatus.ACTIVE,
                DelegationStatus.REVOKED,
                DelegationStatus.CANCELLED,
            },
            DelegationStatus.ACTIVE: {
                DelegationStatus.COMPLETED,
                DelegationStatus.FAILED,
                DelegationStatus.REVOKED,
                DelegationStatus.EXPIRED,
                DelegationStatus.CANCELLED,
            },
            DelegationStatus.COMPLETED: set(),
            DelegationStatus.REJECTED: set(),
            DelegationStatus.REVOKED: set(),
            DelegationStatus.EXPIRED: set(),
            DelegationStatus.FAILED: set(),
            DelegationStatus.CANCELLED: set(),
        }

        valid_next = allowed.get(self.status, set())
        if new_status not in valid_next:
            raise DelegationValidationError(
                f"Invalid delegation status transition from '{self.status.value}' to '{new_status.value}'."
            )
        self.status = new_status
        self.updated_at = datetime.now(tz=UTC)


class DelegatedTask(BaseModel):
    """
    Sub-task assigned to a worker agent under an active delegation.
    """

    task_id: str = Field(default_factory=lambda: f"task-del-{uuid.uuid4()}")
    delegation_id: str
    organization_id: str
    delegator_agent_id: str
    delegate_agent_id: str
    goal: str
    status: str = Field(default="PENDING")
    result: dict[str, Any] | None = Field(default=None)
    failure_reason: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = Field(default=None)
