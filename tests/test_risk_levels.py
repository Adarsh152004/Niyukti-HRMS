"""Tests — Risk Levels."""

from backend.governance.risk import RiskLevel


def test_risk_level_count():
    assert len(RiskLevel) == 4


def test_risk_level_values():
    assert RiskLevel.LOW == "LOW"
    assert RiskLevel.MEDIUM == "MEDIUM"
    assert RiskLevel.HIGH == "HIGH"
    assert RiskLevel.CRITICAL == "CRITICAL"


def test_requires_human_approval():
    assert not RiskLevel.LOW.requires_human_approval
    assert not RiskLevel.MEDIUM.requires_human_approval
    assert RiskLevel.HIGH.requires_human_approval
    assert RiskLevel.CRITICAL.requires_human_approval


def test_requires_ceo_approval():
    assert not RiskLevel.LOW.requires_ceo_approval
    assert not RiskLevel.MEDIUM.requires_ceo_approval
    assert not RiskLevel.HIGH.requires_ceo_approval
    assert RiskLevel.CRITICAL.requires_ceo_approval


def test_numeric_score_ordering():
    assert RiskLevel.LOW.numeric_score < RiskLevel.MEDIUM.numeric_score
    assert RiskLevel.MEDIUM.numeric_score < RiskLevel.HIGH.numeric_score
    assert RiskLevel.HIGH.numeric_score < RiskLevel.CRITICAL.numeric_score


def test_comparison_operators():
    assert RiskLevel.LOW < RiskLevel.MEDIUM
    assert RiskLevel.MEDIUM < RiskLevel.HIGH
    assert RiskLevel.HIGH < RiskLevel.CRITICAL
    assert RiskLevel.CRITICAL > RiskLevel.LOW
    assert RiskLevel.HIGH >= RiskLevel.HIGH
    assert RiskLevel.LOW <= RiskLevel.MEDIUM


def test_governance_invariant_high_risk_requires_approval():
    """Governance invariant: agents cannot bypass approval for HIGH/CRITICAL risk."""
    high_risk_actions = [RiskLevel.HIGH, RiskLevel.CRITICAL]
    for risk in high_risk_actions:
        assert risk.requires_human_approval, f"{risk.value} risk must require human approval"
