"""Tests — Core Multi-Agent Delegation Lifecycle & Creation."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.enums import DelegationStatus
from backend.agents.domain.models import AgentCapability


@pytest.mark.asyncio
async def test_delegation_creation_and_retrieval():
    agent_svc = AgentService()
    del_svc = DelegationService(agent_service=agent_svc)

    cap_read = AgentCapability(capability_id="c1", name="Read Emp", resource="employee", actions=["read"])

    supervisor = await agent_svc.create_agent(
        organization_id="org-acme",
        name="supervisor-1",
        display_name="Supervisor",
        actor_id="act-sup",
        capabilities=[cap_read],
    )
    await agent_svc.activate_agent("org-acme", supervisor.agent_id)

    worker = await agent_svc.create_agent(
        organization_id="org-acme",
        name="worker-1",
        display_name="Worker",
        actor_id="act-wrk",
        capabilities=[],
    )
    await agent_svc.activate_agent("org-acme", worker.agent_id)

    expires_at = datetime.now(tz=UTC) + timedelta(hours=2)

    delegation = await del_svc.create_delegation(
        organization_id="org-acme",
        delegator_agent_id=supervisor.agent_id,
        delegate_agent_id=worker.agent_id,
        parent_task_id="task-root-1",
        requested_capabilities=[cap_read],
        expires_at=expires_at,
    )

    assert delegation.status == DelegationStatus.ACTIVE
    assert len(delegation.capabilities) == 1
    assert delegation.capabilities[0].resource == "employee"

    retrieved = await del_svc.get_delegation("org-acme", delegation.delegation_id)
    assert retrieved is not None
    assert retrieved.delegation_id == delegation.delegation_id
