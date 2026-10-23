"""
Plan Repository Port — Abstract interface for Plan persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.agents.planning.domain.models import Plan


class PlanRepositoryPort(ABC):
    """Abstract repository for persisting and querying Plan domain entities."""

    @abstractmethod
    async def save_plan(self, plan: Plan) -> Plan:
        """Save or update plan."""
        pass

    @abstractmethod
    async def get_plan(self, organization_id: str, plan_id: str) -> Plan | None:
        """Get plan by plan_id within organization."""
        pass

    @abstractmethod
    async def get_plan_for_task(self, organization_id: str, task_id: str) -> Plan | None:
        """Get active plan for task."""
        pass

    @abstractmethod
    async def list_plans_for_agent(self, organization_id: str, agent_id: str) -> Sequence[Plan]:
        """List all plans created for an agent."""
        pass
