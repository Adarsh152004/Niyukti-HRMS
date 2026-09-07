"""
Attendance Application Service — Deterministic daily check-ins, shift alignment, and overtime computations.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.attendance import AttendanceRecord
from backend.hrms.domain.common import AttendanceStatus, utc_now
from backend.hrms.ports.repositories import AttendanceRepository


class AttendanceService(BaseApplicationService):
    """Deterministic, rule-based attendance calculation and check-in management."""

    def __init__(self, attendance_repo: AttendanceRepository) -> None:
        super().__init__()
        self.repo = attendance_repo

    async def log_check_in(
        self,
        organization_id: str,
        employee_id: str,
        record_date: date,
        check_in_time: datetime | None = None,
    ) -> AttendanceRecord:
        """Record employee daily check-in deterministically."""
        existing = await self.repo.get_by_employee_and_date(organization_id, employee_id, record_date)
        now = check_in_time or utc_now()

        if existing:
            existing.check_in_time = now
            existing.status = AttendanceStatus.PRESENT
            existing.updated_at = utc_now()
            return await self.repo.create_or_update(existing)

        record = AttendanceRecord(
            organization_id=organization_id,
            employee_id=employee_id,
            date=record_date,
            check_in_time=now,
            status=AttendanceStatus.PRESENT,
        )
        return await self.repo.create_or_update(record)

    async def log_check_out(
        self,
        organization_id: str,
        employee_id: str,
        record_date: date,
        check_out_time: datetime | None = None,
    ) -> AttendanceRecord:
        """Record check-out and compute total work hours deterministically."""
        existing = await self.repo.get_by_employee_and_date(organization_id, employee_id, record_date)
        now = check_out_time or utc_now()

        if not existing:
            existing = AttendanceRecord(
                organization_id=organization_id,
                employee_id=employee_id,
                date=record_date,
                check_in_time=now,
                status=AttendanceStatus.PRESENT,
            )

        existing.check_out_time = now
        if existing.check_in_time:
            delta_seconds = (existing.check_out_time - existing.check_in_time).total_seconds()
            work_hours = max(0.0, round(delta_seconds / 3600.0, 2))
            existing.work_hours = work_hours
            if work_hours > 8.0:
                existing.overtime_hours = round(work_hours - 8.0, 2)

        existing.updated_at = utc_now()
        return await self.repo.create_or_update(existing)

    async def get_records(
        self,
        organization_id: str,
        employee_id: str,
        start_date: date,
        end_date: date,
    ) -> Sequence[AttendanceRecord]:
        return await self.repo.list_by_employee(organization_id, employee_id, start_date, end_date)
