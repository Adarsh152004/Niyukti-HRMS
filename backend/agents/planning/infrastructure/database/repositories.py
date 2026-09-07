"""
Plan Repositories — InMemory and Postgres implementations for Plan persistence.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.agents.planning.domain.models import Plan
from backend.agents.planning.ports.repositories import PlanRepositoryPort


class InMemoryPlanRepository(PlanRepositoryPort):
    """Thread-safe in-memory repository for unit tests and local execution."""

    def __init__(self) -> None:
        self._plans: dict[str, Plan] = {}

    async def save_plan(self, plan: Plan) -> Plan:
        self._plans[plan.plan_id] = plan.model_copy(deep=True)
        return plan

    async def get_plan(self, organization_id: str, plan_id: str) -> Plan | None:
        plan = self._plans.get(plan_id)
        if plan and plan.organization_id == organization_id:
            return plan.model_copy(deep=True)
        return None

    async def get_plan_for_task(self, organization_id: str, task_id: str) -> Plan | None:
        for plan in self._plans.values():
            if plan.organization_id == organization_id and plan.task_id == task_id:
                return plan.model_copy(deep=True)
        return None

    async def list_plans_for_agent(self, organization_id: str, agent_id: str) -> Sequence[Plan]:
        res = [
            p.model_copy(deep=True)
            for p in self._plans.values()
            if p.organization_id == organization_id and p.agent_id == agent_id
        ]
        res.sort(key=lambda x: x.created_at, reverse=True)
        return res
