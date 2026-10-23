"""Tests — Governance & Safety Control Plane End-to-End Integration."""

import pytest

from backend.agents.application.agent_service import AgentService
from backend.agents.domain.enums import AgentStatus
from backend.agents.governance.application.governance_service import GovernanceService
from backend.agents.governance.domain.enums import ContainmentActionType, GovernanceDecision
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_end_to_end_governance_and_containment_pipeline():
    agent_svc = AgentService()
    gov_svc = GovernanceService(agent_service=agent_svc)

    human_admin = Actor(actor_id="admin-1", actor_type=ActorType.HUMAN, organization_id="org-acme", permissions={"SUPER_ADMIN"})

    # 1. Create and activate agent
    agent = await agent_svc.create_agent("org-acme", "bot-safety-e2e", "Safety Bot E2E", actor_id="act-e2e")
    await agent_svc.activate_agent("org-acme", agent.agent_id)

    # 2. Evaluate normal action
    dec = await gov_svc.evaluate_action("org-acme", agent.agent_id, tool_name="read_employee")
    assert dec == GovernanceDecision.ALLOW

    # 3. Contain agent upon anomaly
    action = await gov_svc.contain_agent(
        organization_id="org-acme",
        agent_id=agent.agent_id,
        action_type=ContainmentActionType.PAUSE,
        reason="Rapid repeated action anomaly detected",
        triggered_by=human_admin,
    )
    assert action.resulting_status == AgentStatus.PAUSED.value

    # 4. Evaluate task trajectory
    evaluation = await gov_svc.evaluate_task("org-acme", agent.agent_id, "task-safety-100")
    assert evaluation.passed is True

    # 5. Resolve containment
    resolved = await gov_svc.resolve_containment("org-acme", agent.agent_id, action.containment_id, resolver_actor=human_admin)
    assert resolved.resulting_status == AgentStatus.ACTIVE.value
