"""Tests — AI Decision Explainability."""

from backend.ai.decision import AIDecision, AIDecisionType
from backend.governance.risk import RiskLevel


def test_ai_decision_creation():
    decision = AIDecision(
        decision_type=AIDecisionType.CANDIDATE_RANKING,
        input_reference_id="app-001",
        input_reference_type="JobApplication",
        decision="Candidate A ranked #1 of 12 applicants",
        confidence=0.91,
        evidence=[
            "5 years relevant experience",
            "87% required skill match",
            "required certification present",
            "relevant project experience",
        ],
        features_used=["experience_years", "skill_match_pct", "certification", "projects"],
        reasoning_summary="Candidate meets all minimum requirements and scores highly on all criteria.",
        model_name="resume-ranking-v1",
        model_version="1.0.0",
        agent_id="agent-ranking-001",
        agent_role="CANDIDATE_RANKING_AGENT",
        risk_level=RiskLevel.LOW,
    )
    assert decision.decision_id is not None
    assert decision.confidence == 0.91
    assert len(decision.evidence) == 4
    assert decision.human_override is False
    assert decision.final_outcome is None


def test_human_override():
    decision = AIDecision(
        decision_type=AIDecisionType.CANDIDATE_RANKING,
        input_reference_id="app-002",
        input_reference_type="JobApplication",
        decision="Candidate B ranked #1",
        confidence=0.78,
        model_name="resume-ranking-v1",
        model_version="1.0.0",
        agent_id="agent-001",
        agent_role="CANDIDATE_RANKING_AGENT",
    )
    assert decision.human_override is False

    decision.apply_human_override(
        reviewer_id="hr-admin-001",
        reason="Candidate B has better culture fit based on interview",
        final_outcome="Candidate B hired — human reviewer confirmed ranking",
    )

    assert decision.human_override is True
    assert decision.overridden_by == "hr-admin-001"
    assert decision.final_outcome is not None
    assert decision.overridden_at is not None


def test_high_confidence_threshold():
    high = AIDecision(
        decision_type=AIDecisionType.ATTRITION_PREDICTION,
        input_reference_id="emp-001",
        input_reference_type="Employee",
        decision="High attrition risk",
        confidence=0.92,
        model_name="attrition-v2",
        model_version="2.0.0",
        agent_id="agent-attrition-001",
        agent_role="ATTRITION_PREDICTION_AGENT",
    )
    low = AIDecision(
        decision_type=AIDecisionType.ATTRITION_PREDICTION,
        input_reference_id="emp-002",
        input_reference_type="Employee",
        decision="Moderate attrition risk",
        confidence=0.65,
        model_name="attrition-v2",
        model_version="2.0.0",
        agent_id="agent-attrition-001",
        agent_role="ATTRITION_PREDICTION_AGENT",
    )
    assert high.is_high_confidence
    assert not low.is_high_confidence


def test_summary_dict_no_pii():
    """Summary dict must not expose raw PII."""
    decision = AIDecision(
        decision_type=AIDecisionType.RESUME_SCREENING,
        input_reference_id="app-003",
        input_reference_type="JobApplication",
        decision="Resume meets requirements",
        confidence=0.88,
        model_name="resume-screen-v1",
        model_version="1.0.0",
        agent_id="agent-screen-001",
        agent_role="RESUME_SCREENING_AGENT",
    )
    summary = decision.summary_dict()
    # Summary must have decision_id but no raw personal data
    assert "decision_id" in summary
    assert "decision" in summary
    assert "confidence" in summary
    assert "email" not in summary
    assert "phone" not in summary


def test_all_decision_types_importable():
    types = [t.value for t in AIDecisionType]
    assert "CANDIDATE_RANKING" in types
    assert "ATTRITION_PREDICTION" in types
    assert "PERFORMANCE_PREDICTION" in types
    assert "SENTIMENT_ANALYSIS" in types
