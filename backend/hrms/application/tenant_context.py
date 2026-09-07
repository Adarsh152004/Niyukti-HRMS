"""
Application Layer — TenantContext abstraction.

TenantContext encapsulates the active tenant ID, acting identity, roles, and permissions
for every incoming application service invocation.

Never infer tenant identity from arbitrary user input — it must be explicitly provided
via resolved TenantContext.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.hrms.domain.actor import Actor, ActorType


class TenantContext(BaseModel):
    """
    Context containing authenticated tenant boundary and acting identity.
    """

    organization_id: str = Field(description="Active tenant ID boundary")
    actor_id: str = Field(description="Acting identity ID (user_id, agent_role, or system)")
    actor_type: ActorType = Field(default=ActorType.HUMAN)
    roles: set[str] = Field(default_factory=set)
    permissions: set[str] = Field(default_factory=set)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_actor(self, identity_tag: str = "") -> Actor:
        """Convert TenantContext to a domain Actor."""
        return Actor(
            actor_id=self.actor_id,
            actor_type=self.actor_type,
            organization_id=self.organization_id,
            identity=identity_tag or self.actor_id,
            roles=self.roles,
            permissions=self.permissions,
        )

    def has_permission(self, permission: str) -> bool:
        """Return True if the tenant context actor possesses the given permission."""
        return permission in self.permissions
