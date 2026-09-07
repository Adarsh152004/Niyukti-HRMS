"""
ApprovalManager — Integrates Agent Orchestrator with Node 5 ApprovalService and HITL Governance.
Enforces exact payload hash verification and prevents agent self-approval.
"""

from __future__ import annotations

import logging

from backend.agents.domain.exceptions import AgentSecurityError
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.commands.application.approval_service import ApprovalService, ApprovalValidationError
from backend.commands.domain.enums import CommandChannel
from backend.commands.domain.models import Command, CommandContext
from backend.hrms.domain.actor import Actor, ActorType
from backend.security.domain.enums import ApprovalStatus
from backend.security.domain.models import ApprovalRequest

logger = logging.getLogger(__name__)


class ApprovalManager:
    """
    Manages Human-In-The-Loop (HITL) approval requests and payload hash consistency.
    """

    def __init__(self, approval_service: ApprovalService | None = None) -> None:
        self.approval_service = approval_service or ApprovalService()

    def create_approval_request(
        self,
        organization_id: str,
        plan: Plan,
        step: PlanStep,
        actor: Actor,
    ) -> ApprovalRequest:
        """Create a HITL approval request for a HIGH or CRITICAL risk plan step."""
        cmd = Command(
            command_type=step.command_type or step.tool_name,
            organization_id=organization_id,
            actor_id=actor.actor_id,
            payload=step.arguments,
        )

        cmd_ctx = CommandContext(
            actor=actor,
            organization_id=organization_id,
            tenant_id=organization_id,
            channel=CommandChannel.WEB,
        )

        request = self.approval_service.create_approval_request(
            command=cmd,
            context=cmd_ctx,
        )
        logger.info(f"Created HITL approval request '{request.request_id}' for step '{step.step_id}'.")
        return request

    def process_approval_decision(
        self,
        organization_id: str,
        request_id: str,
        decision: ApprovalStatus,
        approver: Actor,
        expected_step: PlanStep,
    ) -> tuple[bool, str]:
        """
        Process human approval/rejection decision.
        Enforces that AI Agents CANNOT approve actions and that payload hash matches.
        """
        if approver.actor_type == ActorType.AI_AGENT:
            raise AgentSecurityError("AI Agents are strictly forbidden from approving HITL requests.")

        request = self.approval_service.get_request(request_id)
        if not request:
            return False, f"Approval request '{request_id}' not found."

        # Compute payload hash of current step arguments
        cmd_current = Command(
            command_type=expected_step.command_type or expected_step.tool_name,
            organization_id=organization_id,
            actor_id=approver.actor_id,
            payload=expected_step.arguments,
        )

        try:
            if decision == ApprovalStatus.APPROVED:
                self.approval_service.approve(
                    request_id=request_id,
                    approver_actor=approver,
                    current_command_payload_hash=cmd_current.payload_hash,
                )
                return True, "Approval granted."
            else:
                self.approval_service.reject(
                    request_id=request_id,
                    approver_actor=approver,
                    reason="Human decision rejected.",
                )
                return False, "Approval rejected by human supervisor."
        except ApprovalValidationError as ave:
            return False, f"Approval invalidated: {ave}"
