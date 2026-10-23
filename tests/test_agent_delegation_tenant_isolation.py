"""Tests — Delegation Tenant Isolation & Boundary Safeguards."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.exceptions import DelegationAccessDeniedError
from backend.agents.domain.models import AgentCapability


@pytest.mark.asyncio
async def test_cross_tenant_delegation_rejected():
    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)

    cap_read = AgentCapability(capability_id="c1", name="Read Emp", resource="employee", actions=["read"])

    sup_org_a = await agent_svc.create_agent(
        organization_id="org-a",
        name="sup-org-a",
        display_name="Supervisor A",
        actor_id="act-sup-a",
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-a", sup_org_a.agent_id)

    wrk_org_b = await agent_svc.create_agent(
        organization_id="org-b",
        name="wrk-org-b",
        display_name="Worker B",
        actor_id="act-wrk-b",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-b", wrk_org_b.agent_id)

    expires_at = datetime.now(tz=UTC) + timedelta(hours=2)

    with pytest.raises(DelegationAccessDeniedError, match="not found"):
        await del_svc.create_delegation(
            organization_id="org-a",
            delegator_agent_id=sup_org_a.agent_id,
            delegate_agent_id=wrk_org_b.agent_id,  # Org B agent in Org A request!
            parent_task_id="task-1",
            requested_capabilities=[cap_read],
            expires_at=expires_at,
        )
