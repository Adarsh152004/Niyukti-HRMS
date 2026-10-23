"""
DecisionManager — Converts LLM reasoning output into structured Plan and PlanStep domain models.
"""

from __future__ import annotations

import logging

from backend.agents.planning.domain.enums import StepStatus
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import ReasoningDecision

logger = logging.getLogger(__name__)


class DecisionManager:
    """
    Translates ReasoningDecision outcomes into executable Plan and PlanStep models.
    """

    def create_plan_from_decision(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str,
        objective: str,
        decision: ReasoningDecision,
    ) -> Plan:
        """
        Convert a reasoning decision into a single-step or multi-step Plan.
        """
        steps: list[PlanStep] = []

        if decision.decision_type == DecisionType.TOOL_CALL and decision.selected_tool:
            step = PlanStep(
                sequence=1,
                description=decision.explanation or f"Call tool '{decision.selected_tool}'",
                action_type="TOOL_CALL",
                tool_name=decision.selected_tool,
                arguments=decision.tool_arguments or {},
                dependencies=[],
                status=StepStatus.PENDING,
            )
            steps.append(step)
        elif decision.decision_type in [DecisionType.ANSWER, DecisionType.COMPLETE]:
            step = PlanStep(
                sequence=1,
                description="Complete task with final answer",
                action_type="ANSWER",
                tool_name="system.answer",
                arguments={"final_response": decision.final_response or ""},
                status=StepStatus.COMPLETED,
            )
            steps.append(step)

        return Plan(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
            objective=objective,
            steps=steps,
        )
