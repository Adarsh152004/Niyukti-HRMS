"""Tests — Session management, logout, and revocation."""

from backend.hrms.domain.actor import ActorType
from backend.security.application.session_service import SessionService
from backend.security.domain.enums import AuthenticationChannel


def test_session_lifecycle():
    svc = SessionService()
    sess = svc.create_session(
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
        auth_channel=AuthenticationChannel.WEB,
        user_id="usr-001",
    )
    assert sess.session_id is not None
    assert sess.is_active is True

    # Validate session updates activity timestamp
    validated = svc.validate_session(sess.session_id)
    assert validated.session_id == sess.session_id

    # Revoke single session
    svc.revoke_session(sess.session_id)
    assert sess.is_active is False


def test_logout_all_sessions_for_actor():
    svc = SessionService()
    sess1 = svc.create_session("actor-001", "org-acme", ActorType.HUMAN, AuthenticationChannel.WEB)
    sess2 = svc.create_session("actor-001", "org-acme", ActorType.HUMAN, AuthenticationChannel.CLI)
    sess3 = svc.create_session("actor-002", "org-acme", ActorType.HUMAN, AuthenticationChannel.WEB)

    count = svc.revoke_all_for_actor("actor-001")
    assert count == 2
    assert sess1.is_active is False
    assert sess2.is_active is False
    assert sess3.is_active is True  # actor-002 untouched
