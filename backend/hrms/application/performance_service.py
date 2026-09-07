"""
Performance Application Service — Review cycles, goal management, and appraisal tracking.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.performance import Goal, GoalCategory, ReviewCycle, ReviewCycleStatus
from backend.hrms.ports.repositories import PerformanceRepository


class PerformanceService(BaseApplicationService):
    """Deterministic performance appraisal and goal tracking service."""

    def __init__(self, perf_repo: PerformanceRepository) -> None:
        super().__init__()
        self.repo = perf_repo

    async def create_cycle(
        self,
        organization_id: str,
        name: str,
        start_date: date,
        end_date: date,
        description: str = "",
    ) -> ReviewCycle:
        cycle = ReviewCycle(
            organization_id=organization_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            description=description,
            status=ReviewCycleStatus.ACTIVE,
        )
        return await self.repo.create_cycle(cycle)

    async def create_goal(
        self,
        organization_id: str,
        employee_id: str,
        title: str,
        category: GoalCategory = GoalCategory.INDIVIDUAL,
        weightage: float = 1.0,
        target_value: float | None = None,
    ) -> Goal:
        goal = Goal(
            organization_id=organization_id,
            employee_id=employee_id,
            title=title,
            category=category,
            weightage=weightage,
            target_value=target_value,
        )
        return await self.repo.create_goal(goal)

    async def list_cycles(self, organization_id: str) -> Sequence[ReviewCycle]:
        return await self.repo.list_cycles(organization_id)

    async def list_goals(self, organization_id: str, employee_id: str) -> Sequence[Goal]:
        return await self.repo.list_goals(organization_id, employee_id)
