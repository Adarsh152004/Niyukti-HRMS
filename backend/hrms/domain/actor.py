"""
HRMS Domain — Actor Abstraction.

Actors represent any entity initiating actions or operations in the HRMS.
Actors may be:
- HUMAN: Human user (employee, HR manager, admin, CEO)
- AI_AGENT: Autonomous AI agent (e.g. resume-screening-agent)
- SYSTEM: Background kernel or scheduled job
- EXTERNAL_INTEGRATION: External webhook or integration
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel


class ActorType(StrEnum):
    HUMAN = "HUMAN"
    AI_AGENT = "AI_AGENT"
    SYSTEM = "SYSTEM"
    EXTERNAL_INTEGRATION = "EXTERNAL_INTEGRATION"


class Actor(HRMSBaseModel):
    """
    Representation of an actor performing an operation.
    """

    actor_id: str = Field(description="Unique actor identifier (user_id, agent_role, or system_id)")
    actor_type: ActorType
    organization_id: str = Field(description="Tenant ID boundary")
    identity: str = Field(
        default="", description="Human-readable identity tag e.g. 'john.doe@acme.com' or 'resume-screening-agent'"
    )
    roles: set[str] = Field(default_factory=set, description="Assigned role names or codes")
    permissions: set[str] = Field(
        default_factory=set,
        description="Fine-grained permission codes available to this actor",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_ai_agent(self) -> bool:
        return self.actor_type == ActorType.AI_AGENT

    @property
    def is_human(self) -> bool:
        return self.actor_type == ActorType.HUMAN

    def has_permission(self, permission: str) -> bool:
        """Check if the actor possesses a specific permission."""
        return permission in self.permissions
