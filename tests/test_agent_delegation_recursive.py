"""Tests — Recursive Delegation Policy Enforcement."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.exceptions import RecursiveDelegationDeniedError
from backend.agents.domain.models import AgentCapability


@pytest.mark.asyncio
async def test_recursive_delegation_denied_when_disallowed():
    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)

    cap_read = AgentCapability(capability_id="c1", name="Read Emp", resource="employee", actions=["read"])

    sup = await agent_svc.create_agent(
        organization_id="org-acme",
        name="sup-rec",
        display_name="Sup",
        actor_id="act-sup",
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-acme", sup.agent_id)

    wrk1 = await agent_svc.create_agent(
        organization_id="org-acme",
        name="wrk1-rec",
        display_name="Wrk1",
        actor_id="act-wrk1",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-acme", wrk1.agent_id)

    wrk2 = await agent_svc.create_agent(
        organization_id="org-acme",
        name="wrk2-rec",
        display_name="Wrk2",
        actor_id="act-wrk2",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-acme", wrk2.agent_id)

    expires_at = datetime.now(tz=UTC) + timedelta(hours=2)

    # 1. First delegation with allow_further_delegation = False
    del1 = await del_svc.create_delegation(
        organization_id="org-acme",
        delegator_agent_id=sup.agent_id,
        delegate_agent_id=wrk1.agent_id,
        parent_task_id="task-root",
        requested_capabilities=[cap_read],
        expires_at=expires_at,
        allow_further_delegation=False,  # Explicitly disallow recursive delegation!
    )

    # 2. Worker 1 attempts to delegate further to Worker 2
    with pytest.raises(RecursiveDelegationDeniedError, match="forbids recursive delegation"):
        await del_svc.create_delegation(
            organization_id="org-acme",
            delegator_agent_id=wrk1.agent_id,
            delegate_agent_id=wrk2.agent_id,
            parent_task_id="task-sub",
            requested_capabilities=[cap_read],
            expires_at=expires_at,
            parent_delegation_id=del1.delegation_id,
        )
