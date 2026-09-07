"""Tests — Containment Service Lifecycle Enforcement & Resolution."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.domain.enums import AgentStatus
from backend.agents.governance.application.containment_service import ContainmentService
from backend.agents.governance.domain.enums import ContainmentActionType
from backend.agents.governance.domain.exceptions import GovernanceAccessDeniedError
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_human_can_contain_and_resolve_agent():
    agent_svc = AgentService()
    contain_svc = ContainmentService(agent_service=agent_svc)

    human = Actor(actor_id="admin-human", actor_type=ActorType.HUMAN, organization_id="org-acme", permissions={"SUPER_ADMIN"})

    agent = await agent_svc.create_agent("org-acme", "bot-containable", "Containable Bot", actor_id="act-c")
    await agent_svc.activate_agent("org-acme", agent.agent_id)

    # 1. Execute Pause Containment
    action = await contain_svc.execute_containment(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        action_type=ContainmentActionType.PAUSE,
        reason="Suspicious activity detected",
        triggered_by=human,
    )
    assert action.resulting_status == AgentStatus.PAUSED.value

    # Check updated agent status
    updated = await agent_svc.get_agent("org-acme", agent.agent_id)
    assert updated.status == AgentStatus.PAUSED

    # 2. Resolve Containment
    resolved = await contain_svc.resolve_containment(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        containment_id=action.containment_id,
        resolver_actor=human,
    )
    assert resolved.resulting_status == AgentStatus.ACTIVE.value

    reactivated = await agent_svc.get_agent("org-acme", agent.agent_id)
    assert reactivated.status == AgentStatus.ACTIVE


@pytest.mark.asyncio
async def test_ai_agent_cannot_execute_containment():
    agent_svc = AgentService()
    contain_svc = ContainmentService(agent_service=agent_svc)

    agent_actor = Actor(actor_id="bot-actor", actor_type=ActorType.AI_AGENT, organization_id="org-acme", permissions=set())

    agent = await agent_svc.create_agent("org-acme", "target-bot", "Target Bot", actor_id="act-t")
    await agent_svc.activate_agent("org-acme", agent.agent_id)

    with pytest.raises(GovernanceAccessDeniedError, match="strictly prohibited"):
        await contain_svc.execute_containment(
            organization_id="org-acme",
            agent_id=agent.agent_id,
            action_type=ContainmentActionType.DISABLE,
            reason="Malicious attempt to disable target",
            triggered_by=agent_actor,
        )
