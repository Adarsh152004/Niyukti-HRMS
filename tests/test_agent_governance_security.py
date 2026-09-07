"""Tests — 20 Mandatory Security & Safety Controls for Agent Governance & Safety Control Plane."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.governance.application.audit_service import AuditService
from backend.agents.governance.application.containment_service import ContainmentService
from backend.agents.governance.application.policy_service import GovernancePolicyService
from backend.agents.governance.domain.enums import ContainmentActionType
from backend.agents.governance.domain.exceptions import (
    AgentQuarantinedError,
    GovernanceAccessDeniedError,
)
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_inv_1_agent_cannot_modify_own_governance_policy():
    policy_svc = GovernancePolicyService()
    agent_actor = Actor(actor_id="bot-actor", actor_type=ActorType.AI_AGENT, organization_id="org-acme", permissions=set())

    with pytest.raises(GovernanceAccessDeniedError, match="strictly prohibited"):
        await policy_svc.update_policy("org-acme", "bot-1", actor=agent_actor, max_tool_calls=999)


@pytest.mark.asyncio
async def test_inv_2_agent_cannot_disable_itself_via_containment():
    contain_svc = ContainmentService()
    agent_actor = Actor(actor_id="bot-actor", actor_type=ActorType.AI_AGENT, organization_id="org-acme", permissions=set())

    with pytest.raises(GovernanceAccessDeniedError, match="strictly prohibited"):
        await contain_svc.execute_containment(
            "org-acme", "bot-1", ContainmentActionType.DISABLE, "Self disable", triggered_by=agent_actor
        )


@pytest.mark.asyncio
async def test_inv_3_agent_cannot_re_enable_itself_after_containment():
    contain_svc = ContainmentService()
    agent_actor = Actor(actor_id="bot-actor", actor_type=ActorType.AI_AGENT, organization_id="org-acme", permissions=set())

    with pytest.raises(GovernanceAccessDeniedError, match="strictly prohibited"):
        await contain_svc.resolve_containment("org-acme", "bot-1", "cnt-123", resolver_actor=agent_actor)


@pytest.mark.asyncio
async def test_inv_4_cross_tenant_containment_denied():
    agent_svc = AgentService()
    contain_svc = ContainmentService(agent_service=agent_svc)

    human_org_a = Actor(actor_id="admin-a", actor_type=ActorType.HUMAN, organization_id="org-a", permissions={"SUPER_ADMIN"})

    bot_org_b = await agent_svc.create_agent("org-b", "bot-b", "Bot B", actor_id="act-b")

    with pytest.raises(GovernanceAccessDeniedError, match="organization mismatch"):
        await contain_svc.execute_containment(
            "org-b", bot_org_b.agent_id, ContainmentActionType.PAUSE, "Cross tenant test", triggered_by=human_org_a
        )


@pytest.mark.asyncio
async def test_inv_5_audit_records_contain_no_secrets():
    audit_svc = AuditService()
    rec = await audit_svc.record_audit(
        organization_id="org-acme",
        agent_id="bot-secret",
        event_type="LOGIN",
        action="auth",
        resource="system",
        actor_id="act-1",
        metadata={"user_password": "PlainTextSecret!123", "api_key": "sk-12345"},
    )
    assert rec.metadata["user_password"] == "[REDACTED]"
    assert rec.metadata["api_key"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_inv_6_quarantined_agent_cannot_execute():
    policy_svc = GovernancePolicyService()
    await policy_svc.get_or_create_policy("org-acme", "bot-quarantined")

    await policy_svc.record_violation(
        organization_id="org-acme",
        agent_id="bot-quarantined",
        violation_type="POLICY_BYPASS_ATTEMPT",
        details="Unauthorized action attempt",
    )

    with pytest.raises(AgentQuarantinedError, match="QUARANTINED"):
        await policy_svc.evaluate_execution_policy("org-acme", "bot-quarantined")
