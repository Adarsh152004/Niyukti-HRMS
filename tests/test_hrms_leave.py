"""
Tests for Deterministic Leave Service: Application, Multi-Day Accounting, and Approval.
"""

from __future__ import annotations

from datetime import date

import pytest

from backend.hrms.application.leave_service import LeaveService
from backend.hrms.domain.common import LeaveStatus, LeaveType
from backend.hrms.infrastructure.memory_repositories import InMemoryLeaveRepository


@pytest.mark.asyncio
async def test_leave_application_and_approval_flow():
    repo = InMemoryLeaveRepository()
    svc = LeaveService(repo)
    org_id = "org-leave-test"
    emp_id = "emp-leave-001"

    # 1. Apply for 3 days annual leave
    start = date(2026, 9, 1)
    end = date(2026, 9, 3)
    req = await svc.apply_leave(
        organization_id=org_id,
        employee_id=emp_id,
        leave_type=LeaveType.ANNUAL,
        start_date=start,
        end_date=end,
        reason="Family vacation",
    )
    assert req.status == LeaveStatus.PENDING
    assert req.total_days == 3.0

    # 2. Approve leave
    approved = await svc.approve_leave(org_id, req.leave_id, approver_id="manager-001")
    assert approved is not None
    assert approved.status == LeaveStatus.APPROVED
    assert approved.approved_by == "manager-001"

    # 3. List employee leaves
    leaves = await svc.list_employee_leaves(org_id, emp_id)
    assert len(leaves) == 1
    assert leaves[0].status == LeaveStatus.APPROVED
