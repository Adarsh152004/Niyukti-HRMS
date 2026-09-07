"""
Replanner — Handles plan revision upon recoverable failures.
Enforces security invariant: Security/Authorization/Capability denials CANNOT be bypassed by replanning.
"""

from __future__ import annotations

import logging

from backend.agents.domain.models import Agent, AgentTask
from backend.agents.planning.domain.enums import PlanStatus, StepStatus
from backend.agents.planning.domain.exceptions import ReplanningError
from backend.agents.planning.domain.models import Plan

logger = logging.getLogger(__name__)

SECURITY_DENIAL_KEYWORDS = [
    "unauthorized",
    "access denied",
    "forbidden",
    "permission",
    "lacks capability",
    "authorizationerror",
    "agentsecurityerror",
]


class Replanner:
    """
    Revises Plan steps after recoverable transient failures.
    Blocks attempts to circumvent security policies or capability restrictions via replanning.
    """

    async def create_revised_plan(
        self,
        original_plan: Plan,
        agent: Agent,
        task: AgentTask,
        failure_reason: str,
    ) -> Plan:
        """
        Produce a revised plan version for recoverable errors.
        """
        # Check if failure is due to security/authorization denial
        lower_reason = failure_reason.lower()
        if any(keyword in lower_reason for keyword in SECURITY_DENIAL_KEYWORDS):
            logger.warning(
                f"Security denial detected in plan '{original_plan.plan_id}': '{failure_reason}'. Replanning rejected."
            )
            original_plan.status = PlanStatus.FAILED
            original_plan.failure_reason = f"Security denial cannot be bypassed via replanning: {failure_reason}"
            raise ReplanningError(f"Replanning rejected due to security policy denial: {failure_reason}")

        # Mark original plan as REPLANNING
        original_plan.status = PlanStatus.REPLANNING

        # Build revised plan version with remaining unexecuted steps
        remaining_steps = [s.model_copy(deep=True) for s in original_plan.steps if s.status != StepStatus.COMPLETED]
        for s in remaining_steps:
            if s.status == StepStatus.FAILED:
                s.status = StepStatus.PENDING
                s.retry_count += 1

        revised_plan = Plan(
            plan_id=original_plan.plan_id,
            agent_id=original_plan.agent_id,
            task_id=original_plan.task_id,
            organization_id=original_plan.organization_id,
            status=PlanStatus.DRAFT,
            objective=original_plan.objective,
            steps=remaining_steps,
            current_step=original_plan.current_step,
            version=original_plan.version + 1,
            correlation_id=original_plan.correlation_id,
        )

        return revised_plan
