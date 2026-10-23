"""
Session Management Application Service.

Tracks active user/agent sessions, updates activity timestamps, and handles session revocation.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from backend.hrms.domain.actor import ActorType
from backend.security.domain.enums import AuthenticationChannel
from backend.security.domain.models import Session


class SessionService:
    """
    Service managing active sessions in-memory or via repository.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create_session(
        self,
        actor_id: str,
        organization_id: str,
        actor_type: ActorType,
        auth_channel: AuthenticationChannel,
        user_id: str | None = None,
        agent_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        expire_hours: int = 24,
    ) -> Session:
        """Create and store a new session."""
        now = datetime.now(tz=UTC)
        session = Session(
            actor_id=actor_id,
            organization_id=organization_id,
            actor_type=actor_type,
            auth_channel=auth_channel,
            user_id=user_id,
            agent_id=agent_id,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
            last_seen_at=now,
            expires_at=now + timedelta(hours=expire_hours),
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        """Get session by ID."""
        return self._sessions.get(session_id)

    def validate_session(self, session_id: str) -> Session:
        """Validate session is active and not revoked/expired."""
        session = self._sessions.get(session_id)
        if not session or not session.is_active:
            raise ValueError(f"Session '{session_id}' is invalid, revoked, or expired.")
        session.last_seen_at = datetime.now(tz=UTC)
        return session

    def revoke_session(self, session_id: str) -> Session | None:
        """Revoke a specific session by ID."""
        session = self._sessions.get(session_id)
        if session:
            session.revoked_at = datetime.now(tz=UTC)
        return session

    def revoke_all_for_actor(self, actor_id: str) -> int:
        """Revoke all active sessions for a given actor ID."""
        now = datetime.now(tz=UTC)
        count = 0
        for s in self._sessions.values():
            if s.actor_id == actor_id and s.is_active:
                s.revoked_at = now
                count += 1
        return count

    def list_active_for_actor(self, actor_id: str) -> Sequence[Session]:
        """List all active sessions for an actor."""
        return [s for s in self._sessions.values() if s.actor_id == actor_id and s.is_active]
