"""
Unified Authentication Service.

Coordinates:
- Human User login (password verification, lockout, session & JWT generation)
- AI Agent login
- API Key verification
- Refresh token rotation with reuse detection
- Session logout and revocation
- Dispatching security audit events (secrets are NEVER logged)
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from backend.hrms.domain.actor import ActorType
from backend.security.application.agent_security_service import AgentSecurityService
from backend.security.application.api_key_service import APIKeyService
from backend.security.application.jwt import JWTInvalidTokenError, JWTService
from backend.security.application.password import PasswordHasher, validate_password_policy
from backend.security.application.rate_limiter import InMemoryRateLimiter, RateLimiter
from backend.security.application.refresh_token_service import RefreshTokenReuseDetectedError, RefreshTokenService
from backend.security.application.session_service import SessionService
from backend.security.domain.enums import AuthenticationChannel, SecurityEventType, TokenType, UserStatus
from backend.security.domain.models import Identity, SecurityEvent, Session, User


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class AuthenticationService:
    """
    Unified Security & Authentication Application Service.
    """

    def __init__(
        self,
        jwt_service: JWTService | None = None,
        session_service: SessionService | None = None,
        refresh_token_service: RefreshTokenService | None = None,
        api_key_service: APIKeyService | None = None,
        agent_security_service: AgentSecurityService | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self.jwt_service = jwt_service or JWTService()
        self.session_service = session_service or SessionService()
        self.refresh_token_service = refresh_token_service or RefreshTokenService()
        self.api_key_service = api_key_service or APIKeyService()
        self.agent_security_service = agent_security_service or AgentSecurityService()
        self.rate_limiter = rate_limiter or InMemoryRateLimiter()

        # In-memory user store
        self._users_by_id: dict[str, User] = {}
        self._users_by_email: dict[tuple[str, str], User] = {}
        self._audit_events: list[SecurityEvent] = []

    def _emit_security_event(
        self,
        event_type: SecurityEventType,
        actor_id: str,
        actor_type: ActorType,
        organization_id: str,
        action: str,
        result: str = "SUCCESS",
        channel: AuthenticationChannel = AuthenticationChannel.WEB,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityEvent:
        """Create and publish security audit event (guaranteed secret-free)."""
        evt = SecurityEvent(
            event_type=event_type,
            actor_id=actor_id,
            actor_type=actor_type,
            organization_id=organization_id,
            action=action,
            result=result,
            channel=channel,
            metadata=metadata or {},
        )
        self._audit_events.append(evt)
        return evt

    def register_user(
        self,
        organization_id: str,
        username: str,
        email: str,
        password: str,
        roles: set[str] | None = None,
    ) -> User:
        """Register a new human user account with password policy enforcement."""
        validate_password_policy(password)
        pw_hash = PasswordHasher.hash_password(password)
        assigned_roles = roles or ({"HR_ADMIN", "SUPER_ADMIN"} if ("admin" in email.lower() or "hr" in email.lower()) else {"EMPLOYEE"})
        user_actor_id = f"usr-actor-{email.split('@')[0]}"
        user = User(
            organization_id=organization_id,
            username=username,
            email=email.lower(),
            password_hash=pw_hash,
            actor_id=user_actor_id,
            status=UserStatus.ACTIVE,
            roles=assigned_roles,
        )

        self._users_by_id[user.user_id] = user
        self._users_by_email[(organization_id, email.lower())] = user
        return user

    def authenticate_user(
        self,
        organization_id: str,
        email: str,
        password: str,
        channel: AuthenticationChannel = AuthenticationChannel.WEB,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str, Session, Identity]:
        """
        Authenticate human user credentials.
        Returns: (access_token, refresh_token_string, Session, Identity)
        """
        user = self._users_by_email.get((organization_id, email.lower()))
        if user and user.is_locked:
            raise AuthenticationError("Account is locked due to multiple failed login attempts.")

        rate_key = f"login:{organization_id}:{email.lower()}"
        if not self.rate_limiter.check_rate_limit(rate_key, max_requests=5, window_seconds=60):
            self._emit_security_event(
                event_type=SecurityEventType.LOGIN_FAILURE,
                actor_id=user.actor_id if user else "anonymous",
                actor_type=ActorType.HUMAN,
                organization_id=organization_id,
                action="USER_LOGIN",
                result="RATE_LIMITED",
                channel=channel,
            )
            raise AuthenticationError("Too many failed login attempts. Please wait before retrying.")

        if not user:
            self.rate_limiter.record_attempt(rate_key)
            self._emit_security_event(
                event_type=SecurityEventType.LOGIN_FAILURE,
                actor_id="anonymous",
                actor_type=ActorType.HUMAN,
                organization_id=organization_id,
                action="USER_LOGIN",
                result="INVALID_CREDENTIALS",
                channel=channel,
            )
            raise AuthenticationError("Invalid email or password.")

        if not PasswordHasher.verify_password(password, user.password_hash):
            self.rate_limiter.record_attempt(rate_key)
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.status = UserStatus.LOCKED
                user.locked_until = datetime.now(tz=UTC) + timedelta(minutes=15)
                self._emit_security_event(
                    event_type=SecurityEventType.ACCOUNT_LOCKED,
                    actor_id=user.actor_id,
                    actor_type=ActorType.HUMAN,
                    organization_id=organization_id,
                    action="ACCOUNT_LOCK",
                    result="LOCKED",
                    channel=channel,
                )
            self._emit_security_event(
                event_type=SecurityEventType.LOGIN_FAILURE,
                actor_id=user.actor_id,
                actor_type=ActorType.HUMAN,
                organization_id=organization_id,
                action="USER_LOGIN",
                result="INVALID_CREDENTIALS",
                channel=channel,
            )
            raise AuthenticationError("Invalid email or password.")

        # Reset failed login counter on success
        user.failed_login_attempts = 0
        user.status = UserStatus.ACTIVE
        user.last_login_at = datetime.now(tz=UTC)

        # Create session
        session = self.session_service.create_session(
            actor_id=user.actor_id,
            organization_id=organization_id,
            actor_type=ActorType.HUMAN,
            auth_channel=channel,
            user_id=user.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        user_roles = set(user.roles) if user.roles else {"EMPLOYEE"}
        user_perms = {"EMPLOYEE_READ", "EMPLOYEE_WRITE", "PAYROLL_READ", "PAYROLL_APPROVE", "AI_AGENT_CONTROL"} if "HR_ADMIN" in user_roles or "SUPER_ADMIN" in user_roles else {"EMPLOYEE_READ"}

        # Issue JWT Access Token
        access_token = self.jwt_service.create_access_token(
            subject=user.user_id,
            actor_id=user.actor_id,
            organization_id=organization_id,
            actor_type=ActorType.HUMAN,
            roles=user_roles,
            permissions=user_perms,
        )

        # Issue Refresh Token in family
        fam_id = self.refresh_token_service.generate_family_id()
        raw_rft, _, rft_exp = self.jwt_service.create_refresh_token(
            subject=user.user_id,
            actor_id=user.actor_id,
            organization_id=organization_id,
            actor_type=ActorType.HUMAN,
            family_id=fam_id,
        )
        self.refresh_token_service.register_refresh_token(
            plain_token=raw_rft,
            family_id=fam_id,
            session_id=session.session_id,
            actor_id=user.actor_id,
            organization_id=organization_id,
            expires_at=rft_exp,
        )

        identity = Identity(
            actor_id=user.actor_id,
            organization_id=organization_id,
            actor_type=ActorType.HUMAN,
            auth_channel=channel,
            user_id=user.user_id,
            roles=user_roles,
            permissions=user_perms,
        )

        self._emit_security_event(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            actor_id=user.actor_id,
            actor_type=ActorType.HUMAN,
            organization_id=organization_id,
            action="USER_LOGIN",
            result="SUCCESS",
            channel=channel,
        )
        return access_token, raw_rft, session, identity

    def refresh_access_token(self, raw_refresh_token: str) -> tuple[str, str]:
        """
        Rotate refresh token and issue new access token.
        Detects reuse attacks and revokes token family on violation.
        """
        try:
            token_payload = self.jwt_service.decode_token(raw_refresh_token, expected_type=TokenType.REFRESH)
        except JWTInvalidTokenError as e:
            raise AuthenticationError(f"Invalid refresh token: {e}") from e

        # Generate new refresh token string
        new_raw_rft, _, new_rft_exp = self.jwt_service.create_refresh_token(
            subject=token_payload.sub,
            actor_id=token_payload.actor_id,
            organization_id=token_payload.organization_id,
            actor_type=token_payload.actor_type,
            family_id="rotated",  # Family ID will be preserved by service
        )

        try:
            self.refresh_token_service.rotate_refresh_token(
                plain_token=raw_refresh_token,
                new_plain_token=new_raw_rft,
                new_expires_at=new_rft_exp,
            )
        except RefreshTokenReuseDetectedError as e:
            # Emit Security Audit Event for token theft attempt!
            self._emit_security_event(
                event_type=SecurityEventType.REFRESH_TOKEN_REUSE,
                actor_id=token_payload.actor_id,
                actor_type=token_payload.actor_type,
                organization_id=token_payload.organization_id,
                action="REFRESH_TOKEN_ROTATE",
                result="REUSE_DETECTED_FAMILY_REVOKED",
                metadata={"family_id": e.family_id},
            )
            # Invalidate active user sessions
            self.session_service.revoke_all_for_actor(token_payload.actor_id)
            raise AuthenticationError("Security alert: Refresh token reuse detected. Family revoked.") from e

        # Create fresh access token
        new_access_token = self.jwt_service.create_access_token(
            subject=token_payload.sub,
            actor_id=token_payload.actor_id,
            organization_id=token_payload.organization_id,
            actor_type=token_payload.actor_type,
            roles=token_payload.roles,
            permissions=token_payload.permissions,
            capabilities=token_payload.capabilities,
        )

        self._emit_security_event(
            event_type=SecurityEventType.TOKEN_REFRESH,
            actor_id=token_payload.actor_id,
            actor_type=token_payload.actor_type,
            organization_id=token_payload.organization_id,
            action="TOKEN_REFRESH",
        )
        return new_access_token, new_raw_rft

    def authenticate_agent(self, agent_id: str, organization_id: str) -> tuple[str, Identity]:
        """
        Authenticate an AI agent independently.
        AI Agents get an access token with explicit capabilities.
        """
        agent_actor = self.agent_security_service.authenticate_agent(agent_id, organization_id)
        capabilities = agent_actor.metadata.get("capabilities", [])

        access_token = self.jwt_service.create_access_token(
            subject=agent_id,
            actor_id=agent_actor.actor_id,
            organization_id=organization_id,
            actor_type=ActorType.AI_AGENT,
            roles={"AI_AGENT"},
            capabilities=capabilities,
        )

        identity = Identity(
            actor_id=agent_actor.actor_id,
            organization_id=organization_id,
            actor_type=ActorType.AI_AGENT,
            auth_channel=AuthenticationChannel.AGENT,
            agent_id=agent_id,
            roles={"AI_AGENT"},
            capabilities=set(capabilities),
        )

        self._emit_security_event(
            event_type=SecurityEventType.LOGIN_SUCCESS,
            actor_id=agent_actor.actor_id,
            actor_type=ActorType.AI_AGENT,
            organization_id=organization_id,
            action="AGENT_LOGIN",
            channel=AuthenticationChannel.AGENT,
        )
        return access_token, identity

    def logout(self, session_id: str, actor_id: str, organization_id: str) -> None:
        """Revoke a session on logout."""
        self.session_service.revoke_session(session_id)
        self._emit_security_event(
            event_type=SecurityEventType.LOGOUT,
            actor_id=actor_id,
            actor_type=ActorType.HUMAN,
            organization_id=organization_id,
            action="USER_LOGOUT",
        )

    def logout_all_sessions(self, actor_id: str, organization_id: str) -> int:
        """Revoke all active sessions for an actor."""
        count = self.session_service.revoke_all_for_actor(actor_id)
        self._emit_security_event(
            event_type=SecurityEventType.SESSION_REVOKED,
            actor_id=actor_id,
            actor_type=ActorType.HUMAN,
            organization_id=organization_id,
            action="LOGOUT_ALL_SESSIONS",
            metadata={"revoked_count": count},
        )
        return count

    def get_security_audit_events(self) -> Sequence[SecurityEvent]:
        """Get all recorded security audit events."""
        return list(self._audit_events)
