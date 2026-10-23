"""
Tests for Deterministic Attendance Service: Check-In, Check-Out, and Overtime Computation.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from backend.hrms.application.attendance_service import AttendanceService
from backend.hrms.domain.attendance import AttendanceStatus
from backend.hrms.infrastructure.memory_repositories import InMemoryAttendanceRepository


@pytest.mark.asyncio
async def test_attendance_check_in_and_check_out_overtime_calculation():
    repo = InMemoryAttendanceRepository()
    svc = AttendanceService(repo)
    org_id = "org-attendance-test"
    emp_id = "emp-att-001"
    today = date(2026, 8, 30)

    # 1. Check in at 09:00 UTC
    t_in = datetime(2026, 8, 30, 9, 0, 0, tzinfo=UTC)
    rec1 = await svc.log_check_in(org_id, emp_id, today, check_in_time=t_in)
    assert rec1.status == AttendanceStatus.PRESENT
    assert rec1.check_in_time == t_in
    assert rec1.check_out_time is None

    # 2. Check out at 19:30 UTC (10.5 hours worked -> 2.5 hours overtime)
    t_out = datetime(2026, 8, 30, 19, 30, 0, tzinfo=UTC)
    rec2 = await svc.log_check_out(org_id, emp_id, today, check_out_time=t_out)
    assert rec2.work_hours == 10.5
    assert rec2.overtime_hours == 2.5

    # 3. List records
    history = await svc.get_records(org_id, emp_id, start_date=today, end_date=today)
    assert len(history) == 1
    assert history[0].work_hours == 10.5
