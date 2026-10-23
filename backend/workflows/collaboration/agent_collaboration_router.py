"""
Workflow Agent Collaboration Router — Dispatches workflow events to specialized AI agents for validation and automated execution.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class WorkflowAgentCollaborationRouter:
    """
    Routes active workflow step triggers to the domain's corresponding specialized AI agent:
    - Recruitment Steps → RESUME_SCREENING_AGENT / INTERVIEW_INTELLIGENCE_AGENT
    - Onboarding Steps → ONBOARDING_AGENT
    - Payroll Steps → PAYROLL_ASSISTANT_AGENT
    - Performance Steps → PERFORMANCE_AGENT
    - Policy Steps → COMPLIANCE_AGENT
    """

    _instance: WorkflowAgentCollaborationRouter | None = None

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.event_bus = event_bus or EventBus.get_instance()
        self._command_to_agent_mapping: dict[str, SpecializedAgentRole] = {
            "recruitment.screen_candidates": SpecializedAgentRole.RESUME_SCREENING_AGENT,
            "recruitment.schedule_interview": SpecializedAgentRole.INTERVIEW_INTELLIGENCE_AGENT,
            "it.provision_account": SpecializedAgentRole.ONBOARDING_AGENT,
            "payroll.calculate_cycle": SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT,
            "performance.calibrate": SpecializedAgentRole.PERFORMANCE_AGENT,
            "policy.audit": SpecializedAgentRole.COMPLIANCE_AGENT,
            "skills.identify_gaps": SpecializedAgentRole.SKILL_GAP_AGENT,
            "ml.update_attrition_features": SpecializedAgentRole.ATTRITION_AGENT,
        }

    @classmethod
    def get_instance(cls) -> WorkflowAgentCollaborationRouter:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def resolve_agent_for_command(self, command_type: str) -> SpecializedAgentRole | None:
        """Find the designated specialized AI agent for a workflow command."""
        return self._command_to_agent_mapping.get(command_type)

    async def notify_agent_step_ready(
        self,
        command_type: str,
        workflow_id: str,
        execution_id: str,
        step_id: str,
        payload: dict[str, Any],
    ) -> bool:
        """Publish step readiness event for specialized agent participation."""
        role = self.resolve_agent_for_command(command_type)
        if not role:
            return False

        logger.info(f"Dispatching workflow step [{step_id}] ({command_type}) to Agent [{role.value}]")
        evt = Event(
            event_type="hrms.workflow.agent_assigned",
            source="workflow_engine",
            payload={
                "assigned_agent_role": role.value,
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "step_id": step_id,
                "command_type": command_type,
                "payload": payload,
            },
        )
        await self.event_bus.publish(evt)
        return True
