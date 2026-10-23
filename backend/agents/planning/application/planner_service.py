"""
PlannerService — Application service coordinating Plan creation, validation, persistence, and execution.
"""

from __future__ import annotations

import logging

from backend.agents.application.agent_registry import AgentRegistry
from backend.agents.application.agent_service import AgentService
from backend.agents.application.task_service import AgentTaskService
from backend.agents.planning.application.plan_executor import PlanExecutor
from backend.agents.planning.application.plan_validator import PlanValidator
from backend.agents.planning.application.replanner import Replanner
from backend.agents.planning.domain.enums import PlanStatus
from backend.agents.planning.domain.exceptions import PlanValidationError
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.agents.planning.infrastructure.database.repositories import InMemoryPlanRepository
from backend.agents.planning.ports.repositories import PlanRepositoryPort
from backend.hrms.domain.actor import Actor

logger = logging.getLogger(__name__)


class PlannerService:
    """
    Service managing Plan lifecycle, validation, persistence, execution, and replanning.
    """

    def __init__(
        self,
        plan_repo: PlanRepositoryPort | None = None,
        validator: PlanValidator | None = None,
        executor: PlanExecutor | None = None,
        replanner: Replanner | None = None,
        agent_registry: AgentRegistry | None = None,
        agent_service: AgentService | None = None,
        task_service: AgentTaskService | None = None,
    ) -> None:
        self.plan_repo = plan_repo or InMemoryPlanRepository()
        self.agent_service = agent_service or AgentService()
        self.agent_registry = agent_registry or self.agent_service.registry
        self.task_service = task_service or AgentTaskService()
        self.validator = validator or PlanValidator(registry=self.agent_registry, task_service=self.task_service)
        self.executor = executor or PlanExecutor()
        self.replanner = replanner or Replanner()

    async def create_plan(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str,
        objective: str,
        steps: list[PlanStep],
    ) -> Plan:
        """Create and validate a new plan for task."""
        plan = Plan(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
            objective=objective,
            steps=steps,
            status=PlanStatus.DRAFT,
        )

        report = await self.validator.validate_plan(plan)
        if not report.valid:
            plan.status = PlanStatus.FAILED
            plan.failure_reason = f"Validation failed: {'; '.join(report.errors[:2])}"
            await self.plan_repo.save_plan(plan)
            raise PlanValidationError(plan.failure_reason)

        plan.status = PlanStatus.READY
        await self.plan_repo.save_plan(plan)
        return plan

    async def get_plan(self, organization_id: str, plan_id: str) -> Plan | None:
        """Retrieve plan by ID."""
        return await self.plan_repo.get_plan(organization_id, plan_id)

    async def get_plan_for_task(self, organization_id: str, task_id: str) -> Plan | None:
        """Retrieve active plan for task."""
        return await self.plan_repo.get_plan_for_task(organization_id, task_id)

    async def execute_plan(
        self,
        organization_id: str,
        plan_id: str,
        actor: Actor | None = None,
    ) -> Plan:
        """Execute a validated plan."""
        plan = await self.plan_repo.get_plan(organization_id, plan_id)
        if not plan:
            raise PlanValidationError(f"Plan '{plan_id}' not found.")

        agent = await self.agent_registry.get_agent(organization_id, plan.agent_id)
        task = await self.task_service.get_task(organization_id, plan.task_id)
        if not task:
            raise PlanValidationError(f"Task '{plan.task_id}' not found.")

        executed_plan = await self.executor.execute_plan(
            plan=plan,
            agent=agent,
            task=task,
            actor=actor,
        )

        await self.plan_repo.save_plan(executed_plan)
        return executed_plan

    async def replan(
        self,
        organization_id: str,
        plan_id: str,
        failure_reason: str,
    ) -> Plan:
        """Replan execution following a recoverable transient failure."""
        plan = await self.plan_repo.get_plan(organization_id, plan_id)
        if not plan:
            raise PlanValidationError(f"Plan '{plan_id}' not found.")

        agent = await self.agent_registry.get_agent(organization_id, plan.agent_id)
        task = await self.task_service.get_task(organization_id, plan.task_id)
        if not task:
            raise PlanValidationError(f"Task '{plan.task_id}' not found.")

        revised_plan = await self.replanner.create_revised_plan(
            original_plan=plan,
            agent=agent,
            task=task,
            failure_reason=failure_reason,
        )

        # Save original updated status and save revised plan
        await self.plan_repo.save_plan(plan)
        report = await self.validator.validate_plan(revised_plan, agent=agent, task=task)
        if not report.valid:
            revised_plan.status = PlanStatus.FAILED
            revised_plan.failure_reason = f"Replanned validation failed: {'; '.join(report.errors[:2])}"
            await self.plan_repo.save_plan(revised_plan)
            raise PlanValidationError(revised_plan.failure_reason)

        revised_plan.status = PlanStatus.READY
        await self.plan_repo.save_plan(revised_plan)
        return revised_plan
