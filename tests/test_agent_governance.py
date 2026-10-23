"""Tests — Agent Governance Policy & Quarantine State Machine."""

import pytest

from backend.agents.governance.application.governance_policy_service import GovernancePolicyService
from backend.agents.governance.domain.enums import GovernanceState, ViolationType
from backend.agents.governance.domain.exceptions import AgentQuarantinedError
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_governance_policy_creation_and_retrieval():
    service = GovernancePolicyService()
    policy = await service.get_or_create_policy("org-acme", "agent-10")

    assert policy.governance_state == GovernanceState.ACTIVE
    assert policy.max_reasoning_steps_per_task == 10
    assert policy.auto_quarantine_on_violation is True


@pytest.mark.asyncio
async def test_human_can_update_governance_policy():
    service = GovernancePolicyService()
    human_admin = Actor(
        actor_id="admin-human",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"SUPER_ADMIN"},
    )

    updated = await service.update_policy(
        organization_id="org-acme",
        agent_id="agent-10",
        actor=human_admin,
        max_reasoning_steps=25,
        governance_state=GovernanceState.MONITORED,
    )

    assert updated.max_reasoning_steps_per_task == 25
    assert updated.governance_state == GovernanceState.MONITORED


@pytest.mark.asyncio
async def test_violation_triggers_auto_quarantine():
    service = GovernancePolicyService()
    await service.get_or_create_policy("org-acme", "agent-bad")

    violation = await service.record_violation(
        organization_id="org-acme",
        agent_id="agent-bad",
        violation_type=ViolationType.POLICY_BYPASS_ATTEMPT,
        details="Attempted prohibited action",
    )

    assert violation.action_taken == "QUARANTINED"

    with pytest.raises(AgentQuarantinedError, match="QUARANTINED"):
        await service.validate_agent_execution("org-acme", "agent-bad")
