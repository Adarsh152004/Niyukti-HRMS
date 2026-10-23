"""Tests — Agent Budgets & Quotas Enforcement."""

import pytest

from backend.agents.governance.application.budget_service import BudgetService
from backend.agents.governance.domain.exceptions import BudgetExceededError
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_budget_creation_and_consumption():
    budget_svc = BudgetService()
    human_admin = Actor(
        actor_id="human-1",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"SUPER_ADMIN"},
    )

    await budget_svc.update_budget(
        organization_id="org-acme",
        agent_id="agent-frugal",
        actor=human_admin,
        max_tool_calls=5,
    )

    # Consume 3 tool calls
    b1 = await budget_svc.consume_budget("org-acme", "agent-frugal", tool_calls=3)
    assert b1.tool_calls_count == 3

    # Exceed quota on 3 more calls
    with pytest.raises(BudgetExceededError, match="exceeded"):
        await budget_svc.consume_budget("org-acme", "agent-frugal", tool_calls=3)
