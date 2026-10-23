"""Tests — Governance Policy Service Rule Evaluations & Decisions."""

import pytest

from backend.agents.governance.application.policy_service import GovernancePolicyService
from backend.agents.governance.domain.enums import GovernanceDecision


@pytest.mark.asyncio
async def test_governance_policy_evaluates_prohibited_tools():
    svc = GovernancePolicyService()

    policy = await svc.get_or_create_policy("org-acme", "bot-policy")
    policy.prohibited_tool_categories = ["dangerous", "shell"]
    await svc.repository.save_policy(policy)

    decision = await svc.evaluate_execution_policy("org-acme", "bot-policy", tool_name="dangerous_exec")
    assert decision == GovernanceDecision.DENY

    decision_safe = await svc.evaluate_execution_policy("org-acme", "bot-policy", tool_name="read_employee")
    assert decision_safe == GovernanceDecision.ALLOW


@pytest.mark.asyncio
async def test_governance_policy_requires_approval_for_high_risk():
    svc = GovernancePolicyService()
    decision = await svc.evaluate_execution_policy("org-acme", "bot-policy", risk_level="HIGH")
    assert decision == GovernanceDecision.REQUIRE_APPROVAL
