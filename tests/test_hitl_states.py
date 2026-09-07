"""Tests — HITL States."""

from backend.governance.hitl import HITLPriority, HITLStatus


def test_hitl_status_count():
    """There must be exactly 6 HITL states."""
    assert len(HITLStatus) == 6


def test_hitl_status_values():
    assert HITLStatus.PENDING == "PENDING"
    assert HITLStatus.APPROVED == "APPROVED"
    assert HITLStatus.REJECTED == "REJECTED"
    assert HITLStatus.EXPIRED == "EXPIRED"
    assert HITLStatus.ESCALATED == "ESCALATED"
    assert HITLStatus.CANCELLED == "CANCELLED"


def test_terminal_states():
    assert HITLStatus.APPROVED.is_terminal
    assert HITLStatus.REJECTED.is_terminal
    assert HITLStatus.EXPIRED.is_terminal
    assert HITLStatus.CANCELLED.is_terminal


def test_non_terminal_states():
    assert not HITLStatus.PENDING.is_terminal
    assert not HITLStatus.ESCALATED.is_terminal


def test_hitl_request_creation():
    from backend.governance.hitl import HITLRequest
    from backend.governance.risk import RiskLevel

    req = HITLRequest(
        action_type="candidate_rejection",
        action_description="Reject candidate for Senior Engineer role",
        requesting_agent_id="agent-001",
        requesting_agent_role="CANDIDATE_RANKING_AGENT",
        risk_level=RiskLevel.HIGH,
        priority=HITLPriority.NORMAL,
        resource_type="Candidate",
        resource_id="cand-001",
        required_reviewer_role="HR_MANAGER",
    )
    assert req.status == HITLStatus.PENDING
    assert req.risk_level == RiskLevel.HIGH
    assert req.hitl_id is not None


def test_hitl_decision_creation():
    from backend.governance.hitl import HITLDecision

    decision = HITLDecision(
        hitl_id="req-001",
        reviewer_id="mgr-001",
        reviewer_role="HR_MANAGER",
        decision=HITLStatus.APPROVED,
        approval_reason="Candidate does not meet minimum requirements",
        override_ai_recommendation=False,
    )
    assert decision.decision == HITLStatus.APPROVED
    assert decision.decision_id is not None


def test_human_decision_can_override_ai():
    """Human decisions must be able to override AI recommendations."""
    from backend.governance.hitl import HITLDecision

    override = HITLDecision(
        hitl_id="req-002",
        reviewer_id="hr-admin-001",
        reviewer_role="HR_ADMIN",
        decision=HITLStatus.REJECTED,
        rejection_reason="AI ranking was incorrect — candidate has relevant domain experience",
        override_ai_recommendation=True,
    )
    assert override.override_ai_recommendation is True
    assert override.decision == HITLStatus.REJECTED
