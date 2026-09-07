"""
Security Domain — Core entities for Users, Identities, Sessions, RefreshTokens, APIKeys, AgentIdentities, SecurityEvents, and HITL Primitives.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.hrms.domain.actor import Actor, ActorType
from backend.security.domain.enums import (
    AgentStatus,
    APIKeyStatus,
    ApprovalStatus,
    AuthenticationChannel,
    SecurityEventType,
    UserStatus,
)


def generate_sec_id(prefix: str) -> str:
    """Generate a prefixed random UUID for security entities."""
    return f"{prefix}-{uuid.uuid4()}"


class User(BaseModel):
    """
    Human user security principal entity.
    """

    user_id: str = Field(default_factory=lambda: generate_sec_id("usr"))
    organization_id: str = Field(description="Tenant boundary")
    username: str = Field(description="Username or email identifier")
    email: str = Field(description="User primary email address")
    password_hash: str = Field(description="Securely hashed password (bcrypt/argon2id)")
    actor_id: str = Field(description="Mapped Actor ID")
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    email_verified: bool = Field(default=False)
    roles: set[str] = Field(default_factory=lambda: {"EMPLOYEE"})
    failed_login_attempts: int = Field(default=0)
    locked_until: datetime | None = Field(default=None)
    last_login_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @property
    def is_locked(self) -> bool:
        return bool(self.status == UserStatus.LOCKED and self.locked_until and datetime.now(tz=UTC) < self.locked_until)


class AgentIdentity(BaseModel):
    """
    First-class AI Agent security identity.
    Agents possess explicit capabilities and authenticate independently.
    """

    agent_id: str = Field(default_factory=lambda: generate_sec_id("agent"))
    actor_id: str = Field(description="Mapped Actor ID (ActorType.AI_AGENT)")
    organization_id: str = Field(description="Tenant boundary")
    name: str = Field(description="Agent name e.g. Resume Screening Agent")
    description: str | None = Field(default=None)
    status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    capabilities: set[str] = Field(
        default_factory=set,
        description="Explicit capability grants e.g. {'employee.read', 'resume.screen'}",
    )
    handler_actor_id: str | None = Field(default=None, description="Human handler/CEO actor ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @property
    def is_active(self) -> bool:
        return self.status == AgentStatus.ACTIVE


class ServiceIdentity(BaseModel):
    """
    Internal service or background process identity.
    """

    service_id: str = Field(default_factory=lambda: generate_sec_id("svc"))
    actor_id: str = Field(description="Mapped Actor ID (ActorType.SYSTEM)")
    organization_id: str = Field(description="Tenant boundary")
    name: str = Field(description="Service name e.g. EnterpriseKernel")
    status: str = Field(default="ACTIVE")
    capabilities: set[str] = Field(default_factory=set)


class APIKey(BaseModel):
    """
    Integration API key representation. Raw keys are NEVER stored.
    """

    key_id: str = Field(default_factory=lambda: generate_sec_id("key"))
    organization_id: str = Field(description="Tenant boundary")
    owner_actor_id: str = Field(description="Owner actor ID")
    prefix: str = Field(description="Key prefix displayed to user e.g. hrms_live_abc123")
    key_hash: str = Field(description="SHA-256 hash of secret API key")
    scopes: set[str] = Field(default_factory=set, description="Granted API scopes/capabilities")
    status: APIKeyStatus = Field(default=APIKeyStatus.ACTIVE)
    expires_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    last_used_at: datetime | None = Field(default=None)
    revoked_at: datetime | None = Field(default=None)

    @property
    def is_valid(self) -> bool:
        if self.status != APIKeyStatus.ACTIVE:
            return False
        return not (self.expires_at and datetime.now(tz=UTC) > self.expires_at)


class Session(BaseModel):
    """
    Authenticated user/agent session tracking entity.
    """

    session_id: str = Field(default_factory=lambda: generate_sec_id("sess"))
    actor_id: str = Field(description="Target Actor ID")
    organization_id: str = Field(description="Tenant boundary")
    actor_type: ActorType
    auth_channel: AuthenticationChannel
    user_id: str | None = Field(default=None)
    agent_id: str | None = Field(default=None)
    ip_address: str | None = Field(default=None)
    user_agent: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    expires_at: datetime
    revoked_at: datetime | None = Field(default=None)

    @property
    def is_active(self) -> bool:
        if self.revoked_at is not None:
            return False
        return not datetime.now(tz=UTC) > self.expires_at


class RefreshToken(BaseModel):
    """
    Refresh token rotation tracking. Stores token hash, not plaintext token.
    """

    token_id: str = Field(default_factory=lambda: generate_sec_id("rft"))
    family_id: str = Field(description="Token family ID for reuse detection")
    token_hash: str = Field(description="SHA-256 hash of plaintext refresh token")
    session_id: str = Field(description="Associated session ID")
    actor_id: str = Field(description="Actor ID")
    organization_id: str = Field(description="Tenant boundary")
    expires_at: datetime
    revoked_at: datetime | None = Field(default=None)
    used_at: datetime | None = Field(default=None)

    @property
    def is_valid(self) -> bool:
        if self.revoked_at is not None:
            return False
        if self.used_at is not None:
            return False
        return not datetime.now(tz=UTC) > self.expires_at


class Identity(BaseModel):
    """
    Unified Identity mapping authenticated credentials to an Actor.
    """

    identity_id: str = Field(default_factory=lambda: generate_sec_id("id"))
    actor_id: str = Field(description="Canonical Actor ID")
    organization_id: str = Field(description="Tenant boundary")
    actor_type: ActorType
    auth_channel: AuthenticationChannel
    user_id: str | None = Field(default=None)
    agent_id: str | None = Field(default=None)
    service_id: str | None = Field(default=None)
    api_key_id: str | None = Field(default=None)
    roles: set[str] = Field(default_factory=set)
    permissions: set[str] = Field(default_factory=set)
    capabilities: set[str] = Field(default_factory=set)

    def to_actor(self, identity_tag: str | None = None) -> Actor:
        """Convert Identity snapshot to domain Actor object."""
        tag = identity_tag or f"{self.actor_type.value}:{self.actor_id}"
        return Actor(
            actor_id=self.actor_id,
            actor_type=self.actor_type,
            organization_id=self.organization_id,
            identity=tag,
            roles=self.roles,
            permissions=self.permissions,
            metadata={"capabilities": list(self.capabilities)},
        )


class SecurityEvent(BaseModel):
    """
    Audit log event for security mutations. Secrets are NEVER included.
    """

    event_id: str = Field(default_factory=lambda: generate_sec_id("sec_evt"))
    event_type: SecurityEventType
    actor_id: str
    actor_type: ActorType
    organization_id: str
    action: str
    result: str = Field(default="SUCCESS", description="SUCCESS, FAILURE, DENIED")
    channel: AuthenticationChannel = Field(default=AuthenticationChannel.WEB)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommandAuthorizationContext(BaseModel):
    """
    CEO / Handler command authorization context.
    Consumed by future command bus execution engines.
    """

    actor: Actor
    organization_id: str
    channel: AuthenticationChannel
    permissions: set[str] = Field(default_factory=set)
    capabilities: set[str] = Field(default_factory=set)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hitl_state: str | None = Field(default=None)


class ApprovalRequest(BaseModel):
    """
    HITL Security approval request primitive.
    """

    request_id: str = Field(default_factory=lambda: generate_sec_id("appr"))
    requested_by_actor_id: str
    target_action: str
    target_resource_type: str
    target_resource_id: str
    organization_id: str
    required_permission: str
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    approver_actor_id: str | None = Field(default=None)
    reason: str | None = Field(default=None)
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class ApprovalDecision(BaseModel):
    """
    HITL Security approval decision primitive.
    """

    decision_id: str = Field(default_factory=lambda: generate_sec_id("dec"))
    request_id: str
    approver_actor_id: str
    approved: bool
    reason: str | None = Field(default=None)
    decided_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
