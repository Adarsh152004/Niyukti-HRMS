"""Tests — Delegation Expiration & TTL Enforcement."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_executor import DelegationExecutor
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.enums import DelegationStatus
from backend.agents.delegation.domain.exceptions import DelegationExpiredError
from backend.agents.domain.models import AgentCapability


@pytest.mark.asyncio
async def test_expired_delegation_cannot_execute():
    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)
    executor = DelegationExecutor(delegation_service=del_svc, agent_service=agent_svc)

    cap_read = AgentCapability(capability_id="c1", name="Read Emp", resource="employee", actions=["read"])

    sup = await agent_svc.create_agent(
        organization_id="org-acme",
        name="sup-exp",
        display_name="Sup",
        actor_id="act-sup",
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-acme", sup.agent_id)

    wrk = await agent_svc.create_agent(
        organization_id="org-acme",
        name="wrk-exp",
        display_name="Wrk",
        actor_id="act-wrk",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-acme", wrk.agent_id)

    # Expiration in the past (already expired!)
    expires_at = datetime.now(tz=UTC) - timedelta(seconds=10)

    # Create manual delegation object already expired
    from backend.agents.delegation.domain.models import Delegation

    delegation = Delegation(
        organization_id="org-acme",
        delegator_agent_id=sup.agent_id,
        delegate_agent_id=wrk.agent_id,
        parent_task_id="task-exp-1",
        capabilities=[cap_read],
        status=DelegationStatus.ACTIVE,
        expires_at=expires_at,
    )
    await del_svc.repository.save_delegation(delegation)

    with pytest.raises(DelegationExpiredError, match="EXPIRED"):
        await executor.execute_delegated_task(
            organization_id="org-acme",
            delegation_id=delegation.delegation_id,
            goal="Read employee profile",
        )
