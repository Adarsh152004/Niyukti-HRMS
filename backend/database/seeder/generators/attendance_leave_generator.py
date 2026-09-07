"""
AI-Powered Intelligent HRMS — Attendance & Leave Synthetic Data Generator.

Generates:
- Multi-day / multi-month daily biometric check-in/out records
- Work modes (Office, Remote, Hybrid) and anomaly status
- Leave policies (Annual, Sick, Parental, Casual) and historical requests
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

from backend.database.seeder.generators.employee_generator import SyntheticEmployee


@dataclass
class SyntheticAttendanceRecord:
    id: str
    employee_id: str
    employee_name: str
    organization_id: str
    date: str
    check_in: str
    check_out: str | None
    hours_worked: float
    work_mode: str
    status: str  # PRESENT, LATE, HALF_DAY, ABSENT, ON_LEAVE
    verification_method: str  # BIOMETRIC_GATE, SSO_REMOTE, MOBILE_GEO


@dataclass
class SyntheticLeavePolicy:
    id: str
    organization_id: str
    name: str
    code: str
    annual_days: int
    carry_forward_max: int


@dataclass
class SyntheticLeaveRequest:
    id: str
    employee_id: str
    employee_name: str
    policy_code: str
    start_date: str
    end_date: str
    days: int
    status: str  # APPROVED, PENDING, REJECTED
    reason: str
    approver_name: str | None


def generate_attendance_and_leave(
    employees: list[SyntheticEmployee],
    days_history: int = 30,
    seed: int = 42,
) -> tuple[list[SyntheticAttendanceRecord], list[SyntheticLeavePolicy], list[SyntheticLeaveRequest]]:
    """Generates realistic daily attendance logs and leave requests."""
    rng = random.Random(seed)
    attendance_records: list[SyntheticAttendanceRecord] = []
    leave_requests: list[SyntheticLeaveRequest] = []

    if not employees:
        return [], [], []

    org_id = employees[0].organization_id

    # 1. Leave Policies
    policies = [
        SyntheticLeavePolicy(f"{org_id}-pol-annual", org_id, "Annual Earned Leave", "ANNUAL", 21, 10),
        SyntheticLeavePolicy(f"{org_id}-pol-sick", org_id, "Medical & Sick Leave", "SICK", 12, 0),
        SyntheticLeavePolicy(f"{org_id}-pol-parental", org_id, "Primary Parental Leave", "PARENTAL", 90, 0),
        SyntheticLeavePolicy(f"{org_id}-pol-casual", org_id, "Casual / Personal Leave", "CASUAL", 6, 0),
    ]

    # 2. Daily Attendance Records over recent days
    today = date(2026, 8, 30)

    for d in range(days_history):
        current_date = today - timedelta(days=d)
        # Skip weekends
        if current_date.weekday() >= 5:
            continue

        date_str = current_date.isoformat()

        for emp in employees:
            if emp.status != "active":
                continue

            # 3% chance of on leave, 1% unexpected absence, 96% present
            roll = rng.random()
            if roll < 0.03:
                status = "ON_LEAVE"
                check_in = f"{date_str}T00:00:00Z"
                check_out = None
                hours = 0.0
                method = "POLICY_AUTO"
            elif roll < 0.04:
                status = "ABSENT"
                check_in = f"{date_str}T00:00:00Z"
                check_out = None
                hours = 0.0
                method = "NONE"
            else:
                is_late = rng.random() < 0.08
                status = "LATE" if is_late else "PRESENT"

                in_hour = 9 if not is_late else rng.choice([10, 11])
                in_min = rng.randint(0, 59)
                check_in = f"{date_str}T{in_hour:02d}:{in_min:02d}:00Z"

                out_hour = rng.choice([17, 18, 19])
                out_min = rng.randint(0, 59)
                check_out = f"{date_str}T{out_hour:02d}:{out_min:02d}:00Z"

                hours = max(4.0, (out_hour - in_hour) + (out_min - in_min) / 60.0)
                method = "SSO_REMOTE" if "Remote" in emp.location else "BIOMETRIC_GATE"

            work_mode = "REMOTE" if "Remote" in emp.location else "OFFICE" if "Office" in emp.location else "HYBRID"

            att_id = f"att-{emp.id}-{date_str}"
            attendance_records.append(
                SyntheticAttendanceRecord(
                    id=att_id,
                    employee_id=emp.id,
                    employee_name=emp.full_name,
                    organization_id=org_id,
                    date=date_str,
                    check_in=check_in,
                    check_out=check_out,
                    hours_worked=round(hours, 2),
                    work_mode=work_mode,
                    status=status,
                    verification_method=method,
                )
            )

    # 3. Sample Leave Requests
    reasons = ["Family vacation", "Medical recovery", "Child care", "Personal engagement", "Home relocation"]
    for idx, emp in enumerate(employees[: min(len(employees), 20)]):
        start_d = today + timedelta(days=rng.randint(5, 45))
        duration = rng.choice([1, 2, 3, 5, 10])
        end_d = start_d + timedelta(days=duration)
        pol = rng.choice(policies)

        leave_requests.append(
            SyntheticLeaveRequest(
                id=f"lv-req-{emp.id}-{idx}",
                employee_id=emp.id,
                employee_name=emp.full_name,
                policy_code=pol.code,
                start_date=start_d.isoformat(),
                end_date=end_d.isoformat(),
                days=duration,
                status="APPROVED" if rng.random() > 0.15 else "PENDING",
                reason=rng.choice(reasons),
                approver_name=emp.manager_name or "Alex Rivera",
            )
        )

    return attendance_records, policies, leave_requests
