"""Tests — Delegation Lifecycle Transitions (Approve, Reject, Revoke, Cancel)."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.enums import DelegationStatus
from backend.agents.domain.models import AgentCapability
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_delegation_lifecycle_transitions():
    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)

    cap_hitl = AgentCapability(
        capability_id="c-hitl",
        name="Payroll Update",
        resource="payroll",
        actions=["update"],
        requires_hitl=True,
    )

    sup = await agent_svc.create_agent(
        organization_id="org-acme",
        name="sup-life",
        display_name="Sup",
        actor_id="act-sup",
        capabilities=[cap_hitl],
    )
    await agent_svc.activate_agent("org-acme", sup.agent_id)

    wrk = await agent_svc.create_agent(
        organization_id="org-acme",
        name="wrk-life",
        display_name="Wrk",
        actor_id="act-wrk",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-acme", wrk.agent_id)

    expires_at = datetime.now(tz=UTC) + timedelta(hours=2)

    # 1. Create delegation requiring HITL approval
    delegation = await del_svc.create_delegation(
        organization_id="org-acme",
        delegator_agent_id=sup.agent_id,
        delegate_agent_id=wrk.agent_id,
        parent_task_id="task-root",
        requested_capabilities=[cap_hitl],
        expires_at=expires_at,
    )
    assert delegation.status.value in ["REQUESTED", "APPROVED"]

    # 2. Human Admin Approves
    human_actor = Actor(
        actor_id="human-admin-1",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"SUPER_ADMIN"},
    )
    approved = await del_svc.approve_delegation("org-acme", delegation.delegation_id, approver_actor=human_actor)
    assert approved.status == DelegationStatus.ACTIVE

    # 3. Revoke delegation
    revoked = await del_svc.revoke_delegation("org-acme", delegation.delegation_id, reason="Security audit")
    assert revoked.status == DelegationStatus.REVOKED
