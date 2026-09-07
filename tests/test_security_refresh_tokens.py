"""Tests — Refresh Token rotation, SHA-256 hashed storage, and reuse detection."""

import pytest

from backend.security.application.auth_service import AuthenticationError, AuthenticationService


def test_refresh_token_rotation_success():
    auth_svc = AuthenticationService()
    auth_svc.register_user("org-acme", "alice", "alice@acme.com", "SecretPass123!")
    _, rft1, _, _ = auth_svc.authenticate_user("org-acme", "alice@acme.com", "SecretPass123!")

    # Rotate refresh token
    new_acc, new_rft = auth_svc.refresh_access_token(rft1)
    assert new_acc is not None
    assert new_rft is not None
    assert new_rft != rft1


def test_refresh_token_reuse_detection_revokes_family():
    auth_svc = AuthenticationService()
    auth_svc.register_user("org-acme", "alice", "alice@acme.com", "SecretPass123!")
    _, rft1, session, _ = auth_svc.authenticate_user("org-acme", "alice@acme.com", "SecretPass123!")

    # Rotate once legally
    _, _rft2 = auth_svc.refresh_access_token(rft1)

    # Attempt to REUSE the old rft1 token (simulating an attacker replay attack)
    with pytest.raises(AuthenticationError, match="reuse detected"):
        auth_svc.refresh_access_token(rft1)

    # Session must be revoked immediately
    assert session.is_active is False

    # Security event must record REFRESH_TOKEN_REUSE
    events = auth_svc.get_security_audit_events()
    reuse_evt = next((e for e in events if e.event_type == "REFRESH_TOKEN_REUSE"), None)
    assert reuse_evt is not None
    assert reuse_evt.result == "REUSE_DETECTED_FAMILY_REVOKED"
