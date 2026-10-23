"""
Tests for Collusion & Privilege Escalation Detection across Multi-Agent Teams.
"""

from __future__ import annotations

from backend.agents.operations.governance.collusion_detector import CollusionDetector, CollusionViolationType
from backend.agents.operations.messaging.models import AgentMessage, AgentMessageType
from backend.agents.specialized.domain.enums import SpecializedAgentRole


def test_worker_to_worker_unauthorized_delegation_blocked():
    detector = CollusionDetector.get_instance()
    org_id = "org-collusion-test"

    # Worker (RESUME_SCREENING_AGENT) attempting to delegate task directly to PAYROLL_ASSISTANT_AGENT
    malicious_msg = AgentMessage(
        organization_id=org_id,
        sender_role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
        recipient_role=SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT,
        message_type=AgentMessageType.TASK_DELEGATION,
        payload={"action": "unauthorized_salary_increase"},
    )

    allowed, reason = detector.inspect_message(malicious_msg)
    assert allowed is False
    assert reason is not None
    assert "Worker agent" in reason

    alerts = detector.get_alerts(org_id)
    assert len(alerts) >= 1
    assert alerts[-1].violation_type == CollusionViolationType.UNAUTHORIZED_DELEGATION


def test_supervisor_delegation_allowed():
    detector = CollusionDetector.get_instance()
    org_id = "org-collusion-test"

    valid_msg = AgentMessage(
        organization_id=org_id,
        sender_role=SpecializedAgentRole.RECRUITMENT_AGENT,
        recipient_role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
        message_type=AgentMessageType.TASK_DELEGATION,
        payload={"job_id": "job-500"},
    )

    allowed, reason = detector.inspect_message(valid_msg)
    assert allowed is True
    assert reason is None
