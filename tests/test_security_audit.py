"""Tests — Security audit events dispatching and secret masking."""

from backend.security.application.auth_service import AuthenticationService
from backend.security.domain.enums import SecurityEventType


def test_security_audit_events_emitted_on_auth_operations():
    auth_svc = AuthenticationService()
    auth_svc.register_user("org-acme", "johndoe", "john.doe@acme.com", "SecretPass123!")

    # Login emits LOGIN_SUCCESS event
    _, _, _session, _ = auth_svc.authenticate_user("org-acme", "john.doe@acme.com", "SecretPass123!")

    events = auth_svc.get_security_audit_events()
    assert len(events) > 0
    login_evt = next(e for e in events if e.event_type == SecurityEventType.LOGIN_SUCCESS)
    assert login_evt.organization_id == "org-acme"
    assert login_evt.action == "USER_LOGIN"

    # Ensure passwords, raw tokens, or secrets are NEVER present in audit event payloads/metadata
    evt_str = str(login_evt.model_dump())
    assert "SecretPass123!" not in evt_str
