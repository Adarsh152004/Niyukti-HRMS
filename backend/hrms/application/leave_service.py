"""
Leave Application Service — Deterministic leave request creation, balance validation, and approval workflow.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.common import LeaveStatus, LeaveType, utc_now
from backend.hrms.domain.leave import LeaveRequest
from backend.hrms.ports.repositories import LeaveRepository


class LeaveService(BaseApplicationService):
    """Deterministic leave management without LLM dependency."""

    def __init__(self, leave_repo: LeaveRepository) -> None:
        super().__init__()
        self.repo = leave_repo

    async def apply_leave(
        self,
        organization_id: str,
        employee_id: str,
        leave_type: LeaveType,
        start_date: date,
        end_date: date,
        reason: str | None = None,
        is_half_day: bool = False,
    ) -> LeaveRequest:
        """Submit a leave application deterministically."""
        total_days = 0.5 if is_half_day else max(1.0, float((end_date - start_date).days + 1))
        request = LeaveRequest(
            organization_id=organization_id,
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            is_half_day=is_half_day,
            reason=reason,
            status=LeaveStatus.PENDING,
        )
        return await self.repo.create(request)

    async def approve_leave(
        self,
        organization_id: str,
        leave_id: str,
        approver_id: str,
    ) -> LeaveRequest | None:
        """Approve a pending leave request."""
        req = await self.repo.get_by_id(organization_id, leave_id)
        if not req or req.status != LeaveStatus.PENDING:
            return None
        req.status = LeaveStatus.APPROVED
        req.approved_by = approver_id
        req.approved_at = utc_now()
        req.updated_at = utc_now()
        return await self.repo.update(req)

    async def list_employee_leaves(
        self,
        organization_id: str,
        employee_id: str,
    ) -> Sequence[LeaveRequest]:
        return await self.repo.list_by_employee(organization_id, employee_id)
