"""Tests — Audit Service Secret Redaction & Correlation Tracking."""

import pytest

from backend.agents.governance.application.audit_service import AuditService, redact_secrets


def test_secret_redaction_utility():
    raw = {
        "api_key": "secret-12345",
        "user_password": "super-secret-password",
        "normal_key": "visible-data",
        "nested": {"jwt_token": "bearer-abc"},
    }
    redacted = redact_secrets(raw)

    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["user_password"] == "[REDACTED]"
    assert redacted["normal_key"] == "visible-data"
    assert redacted["nested"]["jwt_token"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_audit_record_creation_with_secret_redaction():
    audit_svc = AuditService()

    record = await audit_svc.record_audit(
        organization_id="org-acme",
        agent_id="bot-audit",
        event_type="TOOL_EXECUTION",
        action="read",
        resource="employee",
        actor_id="act-1",
        metadata={"user_password": "my-secret-password", "query": "emp-100"},
    )

    assert record.metadata["user_password"] == "[REDACTED]"
    assert record.metadata["query"] == "emp-100"
    assert record.correlation_id.startswith("corr-")
