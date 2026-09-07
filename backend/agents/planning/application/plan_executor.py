"""
PlanExecutor — Executes DAG plan steps through ToolExecutionGateway.
Routes state mutations strictly through AgentCommandGateway -> CommandBus.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from backend.agents.application.execution_context import AgentExecutionContextFactory
from backend.agents.domain.models import Agent, AgentExecutionContext, AgentTask
from backend.agents.planning.domain.enums import PlanStatus, StepStatus
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.agents.tools.domain.models import ToolProposal
from backend.hrms.domain.actor import Actor

logger = logging.getLogger(__name__)


class PlanExecutor:
    """
    Executes Plan steps in topological dependency order.
    """

    def __init__(self, tool_gateway: ToolExecutionGateway | None = None) -> None:
        self.tool_gateway = tool_gateway or ToolExecutionGateway()

    async def execute_plan(
        self,
        plan: Plan,
        agent: Agent,
        task: AgentTask,
        actor: Actor | None = None,
        context: AgentExecutionContext | None = None,
    ) -> Plan:
        """
        Execute ready steps of a validated Plan.
        """
        if plan.status in [PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.CANCELLED]:
            return plan

        plan.status = PlanStatus.EXECUTING
        ctx = context or AgentExecutionContextFactory.create_context(agent, task, actor=actor)

        # Topological step execution
        while True:
            ready_step = self._get_next_ready_step(plan)
            if not ready_step:
                break

            ready_step.status = StepStatus.EXECUTING
            proposal = ToolProposal(
                tool_id=ready_step.tool_name,
                arguments=ready_step.arguments,
            )

            try:
                result = await self.tool_gateway.execute_proposal(
                    agent=agent,
                    context=ctx,
                    proposal=proposal,
                )

                if result.status == "SUCCESS":
                    ready_step.status = StepStatus.COMPLETED
                    ready_step.result = result.data or {}
                elif result.status == "WAITING_APPROVAL":
                    ready_step.status = StepStatus.WAITING_APPROVAL
                    ready_step.result = result.data or {}
                    plan.status = PlanStatus.WAITING_APPROVAL
                    logger.info(f"Plan '{plan.plan_id}' step '{ready_step.step_id}' paused for HITL approval.")
                    return plan
                else:
                    ready_step.status = StepStatus.FAILED
                    ready_step.failure_reason = result.error or "Tool execution failed."
                    plan.status = PlanStatus.FAILED
                    plan.failure_reason = ready_step.failure_reason
                    return plan

            except Exception as e:
                ready_step.status = StepStatus.FAILED
                ready_step.failure_reason = str(e)
                plan.status = PlanStatus.FAILED
                plan.failure_reason = f"Step '{ready_step.step_id}' failed: {e}"
                return plan

        # Check if all steps completed
        all_completed = all(s.status == StepStatus.COMPLETED for s in plan.steps)
        if all_completed and plan.steps:
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.now(tz=UTC)

        return plan

    def _get_next_ready_step(self, plan: Plan) -> PlanStep | None:
        """Find next PENDING step whose dependencies are all COMPLETED."""
        completed_step_ids = {s.step_id for s in plan.steps if s.status == StepStatus.COMPLETED}

        for step in plan.steps:
            if step.status == StepStatus.PENDING:
                deps_met = all(dep in completed_step_ids for dep in step.dependencies)
                if deps_met:
                    return step
        return None
