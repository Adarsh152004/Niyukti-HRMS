"""Tests — HITL Governance for High-Risk Delegations."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.enums import DelegationStatus
from backend.agents.domain.models import AgentCapability
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_high_risk_delegation_requires_hitl():
    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)

    cap_critical = AgentCapability(
        capability_id="c-crit",
        name="Critical Terminate",
        resource="employee",
        actions=["terminate"],
        risk_level="CRITICAL",
        requires_hitl=True,
    )

    sup = await agent_svc.create_agent(
        organization_id="org-acme",
        name="sup-crit",
        display_name="Sup",
        actor_id="act-sup",
        capabilities=[cap_critical],
    )
    await agent_svc.activate_agent("org-acme", sup.agent_id)

    wrk = await agent_svc.create_agent(
        organization_id="org-acme",
        name="wrk-crit",
        display_name="Wrk",
        actor_id="act-wrk",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-acme", wrk.agent_id)

    expires_at = datetime.now(tz=UTC) + timedelta(hours=2)

    delegation = await del_svc.create_delegation(
        organization_id="org-acme",
        delegator_agent_id=sup.agent_id,
        delegate_agent_id=wrk.agent_id,
        parent_task_id="task-1",
        requested_capabilities=[cap_critical],
        expires_at=expires_at,
    )

    assert delegation.status == DelegationStatus.REQUESTED

    # Approve with human actor
    human = Actor(
        actor_id="admin-ceo",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"SUPER_ADMIN"},
    )
    approved = await del_svc.approve_delegation("org-acme", delegation.delegation_id, approver_actor=human)
    assert approved.status == DelegationStatus.ACTIVE
