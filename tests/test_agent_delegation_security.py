"""Tests — Multi-Agent Delegation Security Boundaries & Non-Escalation Invariants."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.exceptions import DelegationAccessDeniedError, PrivilegeEscalationError
from backend.agents.domain.models import AgentCapability
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_supervisor_cannot_delegate_unpossessed_capability():
    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)

    cap_read = AgentCapability(capability_id="c1", name="Read Emp", resource="employee", actions=["read"])
    cap_delete = AgentCapability(capability_id="c2", name="Delete Emp", resource="employee", actions=["delete"])

    supervisor = await agent_svc.create_agent(
        organization_id="org-acme",
        name="sup-read-only",
        display_name="Read Only Supervisor",
        actor_id="act-sup",
        capabilities=[cap_read],  # Only has read!
    )
    await agent_svc.activate_agent("org-acme", supervisor.agent_id)

    worker = await agent_svc.create_agent(
        organization_id="org-acme",
        name="worker-target",
        display_name="Worker Target",
        actor_id="act-wrk",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-acme", worker.agent_id)

    expires_at = datetime.now(tz=UTC) + timedelta(hours=2)

    with pytest.raises(PrivilegeEscalationError, match="privilege escalation"):
        await del_svc.create_delegation(
            organization_id="org-acme",
            delegator_agent_id=supervisor.agent_id,
            delegate_agent_id=worker.agent_id,
            parent_task_id="task-1",
            requested_capabilities=[cap_delete],  # Attempting privilege escalation!
            expires_at=expires_at,
        )


@pytest.mark.asyncio
async def test_agent_cannot_approve_own_hitl_delegation():
    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)

    cap_high_risk = AgentCapability(
        capability_id="c-crit",
        name="Payroll Write",
        resource="payroll",
        actions=["update"],
        risk_level="HIGH",
        requires_hitl=True,
    )

    sup = await agent_svc.create_agent(
        organization_id="org-acme",
        name="sup-payroll",
        display_name="Payroll Sup",
        actor_id="act-sup",
        capabilities=[cap_high_risk],
    )
    await agent_svc.activate_agent("org-acme", sup.agent_id)

    wrk = await agent_svc.create_agent(
        organization_id="org-acme",
        name="wrk-payroll",
        display_name="Payroll Wrk",
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
        requested_capabilities=[cap_high_risk],
        expires_at=expires_at,
    )

    assert delegation.status.value in ["REQUESTED", "APPROVED"]

    # Malicious agent actor trying to approve delegation
    agent_actor = Actor(
        actor_id=sup.actor_id,
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
        permissions=set(),
    )

    with pytest.raises(DelegationAccessDeniedError, match="strictly prohibited"):
        await del_svc.approve_delegation("org-acme", delegation.delegation_id, approver_actor=agent_actor)
