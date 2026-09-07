"""
Tests for HR Policy Publishing and Universal Approval Inbox HITL Decisions.
"""

from __future__ import annotations

import pytest

from backend.hrms.application.approval_service import ApprovalInboxService
from backend.hrms.application.policy_service import HRPolicyService
from backend.hrms.domain.approvals import ApprovalStatus, ApprovalType
from backend.hrms.domain.policy import PolicyCategory, PolicyStatus
from backend.hrms.infrastructure.memory_repositories import (
    InMemoryApprovalRepository,
    InMemoryPolicyRepository,
)


@pytest.mark.asyncio
async def test_policy_management_and_approval_inbox():
    p_repo = InMemoryPolicyRepository()
    a_repo = InMemoryApprovalRepository()

    p_svc = HRPolicyService(p_repo)
    a_svc = ApprovalInboxService(a_repo)

    org_id = "org-policy-approval-test"

    # 1. Create policy
    policy = await p_svc.create_policy(
        organization_id=org_id,
        title="Anti-Harassment and Zero-Tolerance Code",
        content="Enterprise standards on respectful and safe workplace conduct.",
        category=PolicyCategory.CODE_OF_CONDUCT,
        version="2.0",
    )
    assert policy.status == PolicyStatus.ACTIVE

    # 2. Submit approval request for policy activation
    req = await a_svc.submit_request(
        organization_id=org_id,
        approval_type=ApprovalType.POLICY_CHANGE,
        requester_id="hr-admin-01",
        requester_role="HR_ADMIN",
        target_entity_id=policy.policy_id,
        payload={"policy_version": "2.0"},
        risk_level="HIGH",
    )
    assert req.status == ApprovalStatus.PENDING

    # 3. Manager approves
    decided = await a_svc.decide_request(
        organization_id=org_id,
        approval_id=req.approval_id,
        approver_id="ceo-001",
        approver_role="CEO",
        decision="APPROVED",
    )
    assert decided is not None
    assert decided.status == ApprovalStatus.APPROVED
    assert len(decided.decisions) == 1
    assert decided.decisions[0].approver_id == "ceo-001"
