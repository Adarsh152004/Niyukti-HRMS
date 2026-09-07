"""Tests — Governance boundaries."""

import pytest

from backend.governance.guardrails import (
    ConfidenceThresholdGuardrail,
    EmergencyStopGuardrail,
    GuardrailChain,
    GuardrailContext,
    GuardrailResult,
    RiskThresholdGuardrail,
)
from backend.governance.risk import RiskLevel


def _make_context(risk_level=RiskLevel.LOW, confidence=0.9):
    return GuardrailContext(
        agent_id="agent-001",
        agent_role="RESUME_SCREENING_AGENT",
        action_type="screen_resume",
        resource_type="JobApplication",
        resource_id="app-001",
        parameters={},
        risk_level=risk_level,
        actor_id="agent-001",
        actor_role="AI_AGENT",
        channel="AUTONOMOUS_AGENT",
        confidence=confidence,
    )


@pytest.mark.asyncio
async def test_low_risk_passes_guardrails():
    chain = GuardrailChain()
    chain.add(RiskThresholdGuardrail())
    chain.add(ConfidenceThresholdGuardrail(min_confidence=0.7))
    chain.add(EmergencyStopGuardrail())
    report = await chain.evaluate(_make_context(RiskLevel.LOW, 0.9))

    assert report.overall_result == GuardrailResult.PASS
    assert not report.is_blocked


@pytest.mark.asyncio
async def test_high_risk_requires_approval():
    chain = GuardrailChain()
    chain.add(RiskThresholdGuardrail())
    report = await chain.evaluate(_make_context(RiskLevel.HIGH))

    assert report.requires_approval
    assert report.overall_result == GuardrailResult.REQUIRE_APPROVAL


@pytest.mark.asyncio
async def test_emergency_stop_blocks_all():
    """Emergency stop must block ALL autonomous actions regardless of risk level."""
    stop_guard = EmergencyStopGuardrail()
    stop_guard.activate()
    chain = GuardrailChain()
    chain.add(stop_guard)
    report = await chain.evaluate(_make_context(RiskLevel.LOW, 0.99))

    assert report.is_blocked
    assert report.overall_result == GuardrailResult.EMERGENCY_STOP


@pytest.mark.asyncio
async def test_low_confidence_requires_approval():
    chain = GuardrailChain()
    chain.add(ConfidenceThresholdGuardrail(min_confidence=0.85))
    report = await chain.evaluate(_make_context(confidence=0.60))

    assert report.requires_approval


@pytest.mark.asyncio
async def test_agent_cannot_bypass_governance():
    """Agents cannot execute governed high-risk actions without approval."""
    chain = GuardrailChain()
    chain.add(RiskThresholdGuardrail())
    report = await chain.evaluate(_make_context(RiskLevel.HIGH))

    assert report.requires_approval or report.is_blocked


def test_governance_contracts_importable():
    from backend.governance.contracts import (
        GovernanceDecision,
        GovernancePolicy,
        GovernanceViolation,
    )

    assert GovernancePolicy is not None
    assert GovernanceDecision is not None
    assert GovernanceViolation is not None
