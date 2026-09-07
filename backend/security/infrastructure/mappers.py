"""
Security Domain ↕ Database Mappers.

Provides bi-directional, deterministic conversion between Security domain models
and SQLAlchemy persistence models.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.hrms.domain.actor import ActorType
from backend.security.domain.enums import (
    AgentStatus,
    APIKeyStatus,
    ApprovalStatus,
    AuthenticationChannel,
    SecurityEventType,
    UserStatus,
)
from backend.security.domain.models import (
    AgentIdentity,
    APIKey,
    ApprovalRequest,
    RefreshToken,
    SecurityEvent,
    Session,
    User,
)
from backend.security.infrastructure.models import (
    AgentIdentityModel,
    APIKeyModel,
    ApprovalRequestModel,
    RefreshTokenModel,
    SecurityEventModel,
    SessionModel,
    UserModel,
)


class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        now = datetime.now(tz=UTC)
        return User(
            user_id=model.id,
            organization_id=model.organization_id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            actor_id=model.actor_id,
            status=UserStatus(model.status),
            email_verified=model.email_verified,
            failed_login_attempts=model.failed_login_attempts,
            locked_until=model.locked_until,
            last_login_at=model.last_login_at,
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: User) -> UserModel:
        return UserModel(
            id=domain.user_id,
            organization_id=domain.organization_id,
            username=domain.username,
            email=domain.email,
            password_hash=domain.password_hash,
            actor_id=domain.actor_id,
            status=domain.status.value,
            email_verified=domain.email_verified,
            failed_login_attempts=domain.failed_login_attempts,
            locked_until=domain.locked_until,
            last_login_at=domain.last_login_at,
        )


class AgentIdentityMapper:
    @staticmethod
    def to_domain(model: AgentIdentityModel) -> AgentIdentity:
        now = datetime.now(tz=UTC)
        return AgentIdentity(
            agent_id=model.id,
            actor_id=model.actor_id,
            organization_id=model.organization_id,
            name=model.name,
            description=model.description,
            status=AgentStatus(model.status),
            capabilities=set(model.capabilities or []),
            handler_actor_id=model.handler_actor_id,
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: AgentIdentity) -> AgentIdentityModel:
        return AgentIdentityModel(
            id=domain.agent_id,
            actor_id=domain.actor_id,
            organization_id=domain.organization_id,
            name=domain.name,
            description=domain.description,
            status=domain.status.value,
            capabilities=list(domain.capabilities),
            handler_actor_id=domain.handler_actor_id,
        )


class APIKeyMapper:
    @staticmethod
    def to_domain(model: APIKeyModel) -> APIKey:
        now = datetime.now(tz=UTC)
        return APIKey(
            key_id=model.id,
            organization_id=model.organization_id,
            owner_actor_id=model.owner_actor_id,
            prefix=model.prefix,
            key_hash=model.key_hash,
            scopes=set(model.scopes or []),
            status=APIKeyStatus(model.status),
            expires_at=model.expires_at,
            created_at=model.created_at or now,
            last_used_at=model.last_used_at,
            revoked_at=model.revoked_at,
        )

    @staticmethod
    def to_model(domain: APIKey) -> APIKeyModel:
        return APIKeyModel(
            id=domain.key_id,
            organization_id=domain.organization_id,
            owner_actor_id=domain.owner_actor_id,
            prefix=domain.prefix,
            key_hash=domain.key_hash,
            scopes=list(domain.scopes),
            status=domain.status.value,
            expires_at=domain.expires_at,
            last_used_at=domain.last_used_at,
            revoked_at=domain.revoked_at,
        )


class SessionMapper:
    @staticmethod
    def to_domain(model: SessionModel) -> Session:
        return Session(
            session_id=model.id,
            actor_id=model.actor_id,
            organization_id=model.organization_id,
            actor_type=ActorType(model.actor_type),
            auth_channel=AuthenticationChannel(model.auth_channel),
            user_id=model.user_id,
            agent_id=model.agent_id,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            created_at=model.created_at,
            last_seen_at=model.last_seen_at,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
        )

    @staticmethod
    def to_model(domain: Session) -> SessionModel:
        return SessionModel(
            id=domain.session_id,
            actor_id=domain.actor_id,
            organization_id=domain.organization_id,
            actor_type=domain.actor_type.value,
            auth_channel=domain.auth_channel.value,
            user_id=domain.user_id,
            agent_id=domain.agent_id,
            ip_address=domain.ip_address,
            user_agent=domain.user_agent,
            created_at=domain.created_at,
            last_seen_at=domain.last_seen_at,
            expires_at=domain.expires_at,
            revoked_at=domain.revoked_at,
        )


class RefreshTokenMapper:
    @staticmethod
    def to_domain(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            token_id=model.id,
            family_id=model.family_id,
            token_hash=model.token_hash,
            session_id=model.session_id,
            actor_id=model.actor_id,
            organization_id=model.organization_id,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            used_at=model.used_at,
        )

    @staticmethod
    def to_model(domain: RefreshToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            id=domain.token_id,
            family_id=domain.family_id,
            token_hash=domain.token_hash,
            session_id=domain.session_id,
            actor_id=domain.actor_id,
            organization_id=domain.organization_id,
            expires_at=domain.expires_at,
            revoked_at=domain.revoked_at,
            used_at=domain.used_at,
        )


class SecurityEventMapper:
    @staticmethod
    def to_domain(model: SecurityEventModel) -> SecurityEvent:
        return SecurityEvent(
            event_id=model.id,
            event_type=SecurityEventType(model.event_type),
            actor_id=model.actor_id,
            actor_type=ActorType(model.actor_type),
            organization_id=model.organization_id,
            action=model.action,
            result=model.result,
            channel=AuthenticationChannel(model.channel),
            request_id=model.request_id,
            correlation_id=model.correlation_id,
            occurred_at=model.occurred_at,
            metadata=model.metadata_json or {},
        )

    @staticmethod
    def to_model(domain: SecurityEvent) -> SecurityEventModel:
        return SecurityEventModel(
            id=domain.event_id,
            event_type=domain.event_type.value,
            actor_id=domain.actor_id,
            actor_type=domain.actor_type.value,
            organization_id=domain.organization_id,
            action=domain.action,
            result=domain.result,
            channel=domain.channel.value,
            request_id=domain.request_id,
            correlation_id=domain.correlation_id,
            occurred_at=domain.occurred_at,
            metadata_json=domain.metadata,
        )


class ApprovalRequestMapper:
    @staticmethod
    def to_domain(model: ApprovalRequestModel) -> ApprovalRequest:
        now = datetime.now(tz=UTC)
        return ApprovalRequest(
            request_id=model.id,
            requested_by_actor_id=model.requested_by_actor_id,
            target_action=model.target_action,
            target_resource_type=model.target_resource_type,
            target_resource_id=model.target_resource_id,
            organization_id=model.organization_id,
            required_permission=model.required_permission,
            status=ApprovalStatus(model.status),
            approver_actor_id=model.approver_actor_id,
            reason=model.reason,
            expires_at=model.expires_at,
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: ApprovalRequest) -> ApprovalRequestModel:
        return ApprovalRequestModel(
            id=domain.request_id,
            requested_by_actor_id=domain.requested_by_actor_id,
            target_action=domain.target_action,
            target_resource_type=domain.target_resource_type,
            target_resource_id=domain.target_resource_id,
            organization_id=domain.organization_id,
            required_permission=domain.required_permission,
            status=domain.status.value,
            approver_actor_id=domain.approver_actor_id,
            reason=domain.reason,
            expires_at=domain.expires_at,
        )
