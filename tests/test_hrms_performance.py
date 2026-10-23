"""
Tests for Deterministic Performance Appraisal Service: Review Cycles and Goal Tracking.
"""

from __future__ import annotations

from datetime import date

import pytest

from backend.hrms.application.performance_service import PerformanceService
from backend.hrms.domain.performance import GoalCategory, ReviewCycleStatus
from backend.hrms.infrastructure.memory_repositories import InMemoryPerformanceRepository


@pytest.mark.asyncio
async def test_performance_review_cycles_and_goals():
    repo = InMemoryPerformanceRepository()
    svc = PerformanceService(repo)
    org_id = "org-performance-test"
    emp_id = "emp-perf-001"

    # 1. Create review cycle
    cycle = await svc.create_cycle(
        organization_id=org_id,
        name="Annual Review 2026",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        description="Enterprise yearly appraisal cycle",
    )
    assert cycle.status == ReviewCycleStatus.ACTIVE

    # 2. Create goal
    goal = await svc.create_goal(
        organization_id=org_id,
        employee_id=emp_id,
        title="Reduce API p99 latency to under 50ms",
        category=GoalCategory.TECHNICAL,
        weightage=2.0,
        target_value=50.0,
    )
    assert goal.title == "Reduce API p99 latency to under 50ms"

    # 3. List
    cycles = await svc.list_cycles(org_id)
    goals = await svc.list_goals(org_id, emp_id)
    assert len(cycles) == 1
    assert len(goals) == 1
