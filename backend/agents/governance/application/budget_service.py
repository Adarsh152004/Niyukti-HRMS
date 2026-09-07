"""
Budget Service — Tracks agent resource consumption, token usage, and enforces budget quotas.
"""

from __future__ import annotations

import logging

from backend.agents.governance.domain.exceptions import BudgetExceededError, GovernanceAccessDeniedError
from backend.agents.governance.domain.models import AgentBudget
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.hrms.domain.actor import Actor, ActorType
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class BudgetService:
    """
    Manages tenant and agent resource budgets and quota tracking.
    """

    def __init__(
        self,
        repository: GovernanceRepositoryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository = repository or InMemoryGovernanceRepository()
        self.event_bus = event_bus or EventBus.get_instance()

    async def get_or_create_budget(self, organization_id: str, agent_id: str) -> AgentBudget:
        """Get or initialize budget record for agent."""
        budget = await self.repository.get_budget(organization_id, agent_id)
        if not budget:
            budget = AgentBudget(
                organization_id=organization_id,
                agent_id=agent_id,
            )
            await self.repository.save_budget(budget)
        return budget

    async def update_budget(
        self,
        organization_id: str,
        agent_id: str,
        actor: Actor,
        max_token_budget: int | None = None,
        max_tool_calls: int | None = None,
        max_reasoning_runs: int | None = None,
        max_command_executions: int | None = None,
    ) -> AgentBudget:
        """
        Update agent budget.
        SECURITY INVARIANT: Approver MUST be HUMAN. AI Agents cannot modify budgets!
        """
        if actor.actor_type == ActorType.AI_AGENT:
            raise GovernanceAccessDeniedError("AI Agents are strictly prohibited from modifying budgets or quotas.")

        if actor.organization_id != organization_id:
            raise GovernanceAccessDeniedError("Actor organization mismatch.")

        budget = await self.get_or_create_budget(organization_id, agent_id)

        if max_token_budget is not None:
            budget.max_token_budget = max_token_budget
        if max_tool_calls is not None:
            budget.max_tool_calls = max_tool_calls
        if max_reasoning_runs is not None:
            budget.max_reasoning_runs = max_reasoning_runs
        if max_command_executions is not None:
            budget.max_command_executions = max_command_executions

        return await self.repository.save_budget(budget)

    async def consume_budget(
        self,
        organization_id: str,
        agent_id: str,
        tokens: int = 0,
        tool_calls: int = 0,
        reasoning_runs: int = 0,
        command_executions: int = 0,
    ) -> AgentBudget:
        """
        Consume budget quotas and enforce limits.
        Raises BudgetExceededError if limit breached.
        """
        budget = await self.get_or_create_budget(organization_id, agent_id)

        budget.tokens_consumed += tokens
        budget.tool_calls_count += tool_calls
        budget.reasoning_runs_count += reasoning_runs
        budget.command_executions_count += command_executions

        if budget.is_exhausted():
            await self.repository.save_budget(budget)
            await self.event_bus.publish(
                Event(
                    event_type="hrms.agent.budget_exceeded",
                    source="budget_service",
                    payload={
                        "agent_id": agent_id,
                        "organization_id": organization_id,
                        "tokens_consumed": budget.tokens_consumed,
                        "tool_calls": budget.tool_calls_count,
                    },
                )
            )
            raise BudgetExceededError(f"Resource budget or quota exceeded for agent '{agent_id}'.")

        return await self.repository.save_budget(budget)
