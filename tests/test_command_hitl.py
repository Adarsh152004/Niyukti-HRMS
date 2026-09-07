"""Tests — HITL Approval Gate, self-approval prevention, cross-tenant check, and payload hash binding."""

import pytest

from backend.commands.application.approval_service import ApprovalService, ApprovalValidationError
from backend.commands.application.bus import CommandBus
from backend.commands.application.handlers import TerminateEmployeeCommandHandler
from backend.commands.domain.enums import CommandStatus, RiskLevel
from backend.commands.domain.models import Command, CommandMetadata
from backend.hrms.domain.actor import Actor, ActorType


@pytest.mark.asyncio
async def test_high_risk_command_triggers_hitl_approval_gate():
    bus = CommandBus()
    handler = TerminateEmployeeCommandHandler()
    meta = CommandMetadata(
        command_type="employee.terminate",
        description="Terminate employee",
        required_permissions=["EMPLOYEE_DELETE"],
        risk_level=RiskLevel.HIGH,
        requires_approval=True,
    )
    bus.registry.register("employee.terminate", handler, meta)

    actor = Actor(
        actor_id="usr-actor-001",
        actor_type=ActorType.HUMAN,
        organization_id="org-acme",
        permissions={"EMPLOYEE_DELETE"},
    )
    cmd = Command(
        command_type="employee.terminate",
        actor_id=actor.actor_id,
        organization_id=actor.organization_id,
        payload={"employee_id": "emp-101"},
    )

    ctx = bus.build_context(actor)
    res = await bus.dispatch(cmd, ctx)

    assert res.status == CommandStatus.WAITING_APPROVAL
    assert "approval_request_id" in res.result_data

    # Check pending approvals in service
    pending = bus.approval_service.list_pending_for_organization("org-acme")
    assert len(pending) == 1
    assert pending[0].requested_by_actor_id == "usr-actor-001"


def test_self_approval_strictly_blocked():
    appr_svc = ApprovalService()
    requester = Actor(actor_id="actor-001", actor_type=ActorType.HUMAN, organization_id="org-acme")
    cmd = Command(command_type="employee.terminate", actor_id="actor-001", organization_id="org-acme")

    ctx = CommandBus().build_context(requester)
    req = appr_svc.create_approval_request(cmd, ctx)

    # Requester trying to approve their own request must fail!
    with pytest.raises(ApprovalValidationError, match="Self-approval violation"):
        appr_svc.approve(req.request_id, approver_actor=requester)


def test_cross_tenant_approval_blocked():
    appr_svc = ApprovalService()
    requester = Actor(actor_id="actor-001", actor_type=ActorType.HUMAN, organization_id="org-acme-a")
    cmd = Command(command_type="employee.terminate", actor_id="actor-001", organization_id="org-acme-a")

    ctx = CommandBus().build_context(requester)
    req = appr_svc.create_approval_request(cmd, ctx)

    approver_org_b = Actor(actor_id="actor-002", actor_type=ActorType.HUMAN, organization_id="org-acme-b")
    with pytest.raises(ApprovalValidationError, match="Cross-tenant approval"):
        appr_svc.approve(req.request_id, approver_actor=approver_org_b)


def test_modified_payload_hash_invalidates_approval():
    appr_svc = ApprovalService()
    requester = Actor(actor_id="actor-001", actor_type=ActorType.HUMAN, organization_id="org-acme")
    cmd = Command(
        command_type="employee.terminate",
        actor_id="actor-001",
        organization_id="org-acme",
        payload={"employee_id": "emp-101"},
    )

    ctx = CommandBus().build_context(requester)
    req = appr_svc.create_approval_request(cmd, ctx)

    approver = Actor(actor_id="actor-002-ceo", actor_type=ActorType.HUMAN, organization_id="org-acme")

    # Presenting a modified payload hash during approval must be rejected
    tampered_payload_hash = "modified_hash_12345"
    with pytest.raises(ApprovalValidationError, match="modified"):
        appr_svc.approve(req.request_id, approver_actor=approver, current_command_payload_hash=tampered_payload_hash)
