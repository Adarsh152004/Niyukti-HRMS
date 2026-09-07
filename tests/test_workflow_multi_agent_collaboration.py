"""
Tests for Multi-Agent Workflow Event Collaboration and Specialized Routing.
"""

from __future__ import annotations

import pytest

from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.workflows.collaboration.agent_collaboration_router import WorkflowAgentCollaborationRouter


@pytest.mark.asyncio
async def test_workflow_agent_collaboration_routing():
    router = WorkflowAgentCollaborationRouter.get_instance()

    # 1. Resolve agent for recruitment command
    role1 = router.resolve_agent_for_command("recruitment.screen_candidates")
    assert role1 == SpecializedAgentRole.RESUME_SCREENING_AGENT

    # 2. Resolve agent for payroll calculation
    role2 = router.resolve_agent_for_command("payroll.calculate_cycle")
    assert role2 == SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT

    # 3. Notify agent readiness
    dispatched = await router.notify_agent_step_ready(
        command_type="recruitment.screen_candidates",
        workflow_id="wf-rec-01",
        execution_id="exec-rec-01",
        step_id="step_screen_resumes",
        payload={"requisition_id": "req-999"},
    )
    assert dispatched is True
