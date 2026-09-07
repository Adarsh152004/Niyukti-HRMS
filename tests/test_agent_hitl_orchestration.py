"""Tests — ApprovalManager HITL integration, payload hash binding, and self-approval block."""

import pytest

from backend.agents.domain.exceptions import AgentSecurityError
from backend.agents.orchestration.application.approval_manager import ApprovalManager
from backend.agents.planning.domain.models import Plan, PlanStep
from backend.commands.application.approval_service import ApprovalService
from backend.hrms.domain.actor import Actor, ActorType
from backend.security.domain.enums import ApprovalStatus


@pytest.mark.asyncio
async def test_approval_manager_high_risk_step_triggers_approval_request():
    approval_svc = ApprovalService()
    manager = ApprovalManager(approval_service=approval_svc)

    step = PlanStep(
        sequence=1,
        description="Terminate employee",
        tool_name="employee.terminate",
        command_type="employee.terminate",
        arguments={"employee_id": "emp-bad"},
        requires_approval=True,
        risk_level="HIGH",
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        objective="Terminate non-compliant employee",
        steps=[step],
    )

    agent_actor = Actor(
        actor_id="actor-agent-1",
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
    )

    req = manager.create_approval_request("org-acme", plan, step, agent_actor)
    assert req.request_id.startswith("req-") or len(req.request_id) > 0
    assert req.target_action == "employee.terminate"


@pytest.mark.asyncio
async def test_approval_manager_agent_self_approval_blocked():
    approval_svc = ApprovalService()
    manager = ApprovalManager(approval_service=approval_svc)

    step = PlanStep(
        sequence=1,
        description="Terminate employee",
        tool_name="employee.terminate",
        command_type="employee.terminate",
        arguments={"employee_id": "emp-bad"},
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        objective="Self termination attempt",
        steps=[step],
    )

    agent_actor = Actor(
        actor_id="actor-agent-1",
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
    )

    req = manager.create_approval_request("org-acme", plan, step, agent_actor)

    # Attempting to approve using AI_AGENT actor throws AgentSecurityError
    with pytest.raises(AgentSecurityError, match="strictly forbidden from approving"):
        manager.process_approval_decision(
            organization_id="org-acme",
            request_id=req.request_id,
            decision=ApprovalStatus.APPROVED,
            approver=agent_actor,
            expected_step=step,
        )


@pytest.mark.asyncio
async def test_approval_manager_payload_hash_modification_invalidates_approval():
    approval_svc = ApprovalService()
    manager = ApprovalManager(approval_service=approval_svc)

    original_step = PlanStep(
        sequence=1,
        description="Terminate employee",
        tool_name="employee.terminate",
        command_type="employee.terminate",
        arguments={"employee_id": "emp-bad"},
    )

    plan = Plan(
        organization_id="org-acme",
        agent_id="agent-1",
        task_id="task-1",
        objective="Terminate employee",
        steps=[original_step],
    )

    agent_actor = Actor(
        actor_id="actor-agent-1",
        actor_type=ActorType.AI_AGENT,
        organization_id="org-acme",
    )
    human_actor = Actor(
        actor_id="actor-human-1",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
    )

    req = manager.create_approval_request("org-acme", plan, original_step, agent_actor)

    # Modify step arguments after approval request creation
    modified_step = PlanStep(
        sequence=1,
        description="Terminate employee",
        tool_name="employee.terminate",
        command_type="employee.terminate",
        arguments={"employee_id": "emp-DIFFERENT"},  # Modified payload!
    )

    success, msg = manager.process_approval_decision(
        organization_id="org-acme",
        request_id=req.request_id,
        decision=ApprovalStatus.APPROVED,
        approver=human_actor,
        expected_step=modified_step,
    )

    assert not success
    assert "Approval invalidated" in msg
