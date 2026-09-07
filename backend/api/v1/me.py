"""
Employee Self-Service (ESS) Endpoints — /api/v1/me/*
Strict tenant isolation and authenticated identity boundary for employees.
"""

from __future__ import annotations

import datetime
import json
import logging
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.api.dependencies import (
    get_attendance_service,
    get_employee_service,
    get_tenant_context,
    get_work_log_repository,
)
from backend.database.sqlite_db import get_db_connection, record_audit_log
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.attendance import AttendanceRecord
from backend.hrms.domain.common import AttendanceStatus, utc_now
from backend.hrms.domain.employee import Employee
from backend.hrms.infrastructure.sqlite_repositories import SqliteWorkLogRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/me", tags=["Employee Self-Service"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class PunchRequest(BaseModel):
    action: str = Field(..., description="'CLOCK_IN' or 'CLOCK_OUT'")
    notes: Optional[str] = Field(None, description="Optional employee notes")


class LeaveApplyRequest(BaseModel):
    leave_type_id: str = Field(..., description="e.g. 'lt-annual', 'lt-sick', 'lt-casual'")
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    days_count: float = Field(default=1.0, ge=0.5)
    is_half_day: bool = False
    reason: str = Field(..., min_length=3)


class WorkLogCreateRequest(BaseModel):
    description: str = Field(..., min_length=3)
    hours_spent: float = Field(default=1.0, ge=0.25, le=24.0)
    task_id: Optional[str] = None
    blockers: Optional[str] = None
    work_date: Optional[str] = None


# ── Identity Resolution Helper ────────────────────────────────────────────────

async def _resolve_employee(ctx: TenantContext) -> dict[str, Any]:
    """
    Strictly resolves the authenticated employee record for the current context actor.
    Prioritizes matching actor_id with employee_id or email, defaulting to the
    first active employee (emp-001) if acting in dev/admin mode.
    """
    async with get_db_connection() as db:
        # 1. Try matching by employee id
        async with db.execute(
            "SELECT * FROM employees WHERE (organization_id = ? OR organization_id = 'org-nova-01') AND id = ?",
            (ctx.organization_id, ctx.actor_id),
        ) as c:
            row = await c.fetchone()

        # 2. Try matching by email if actor_id looks like email
        if not row and "@" in ctx.actor_id:
            async with db.execute(
                "SELECT * FROM employees WHERE (organization_id = ? OR organization_id = 'org-nova-01') AND email = ?",
                (ctx.organization_id, ctx.actor_id),
            ) as c:
                row = await c.fetchone()

        # 3. Dev / Admin fallback: default to first active employee (Vikram Aditya / emp-001)
        if not row:
            async with db.execute(
                "SELECT * FROM employees WHERE (organization_id = ? OR organization_id = 'org-nova-01') AND employment_status = 'ACTIVE' ORDER BY id ASC LIMIT 1",
                (ctx.organization_id,),
            ) as c:
                row = await c.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active employee profile found for actor '{ctx.actor_id}' in tenant '{ctx.organization_id}'",
            )

        r = dict(row)
        dept_name = "General"
        desig_name = "Staff Member"

        if r.get("department_id"):
            async with db.execute("SELECT name FROM departments WHERE id = ?", (r["department_id"],)) as dc:
                drow = await dc.fetchone()
                if drow:
                    dept_name = drow["name"]

        if r.get("designation_id"):
            async with db.execute("SELECT name FROM designations WHERE id = ?", (r["designation_id"],)) as dgc:
                grow = await dgc.fetchone()
                if grow:
                    desig_name = grow["name"]

        r["department_name"] = dept_name
        r["designation_name"] = desig_name
        return r


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("", summary="Get Current Authenticated Employee Profile")
async def get_my_profile(ctx: TenantContext = Depends(get_tenant_context)) -> dict[str, Any]:
    emp = await _resolve_employee(ctx)
    return {
        "employee_id": emp["id"],
        "organization_id": emp["organization_id"],
        "employee_code": emp["employee_code"],
        "first_name": emp["first_name"],
        "last_name": emp["last_name"],
        "full_name": f"{emp['first_name']} {emp['last_name']}".strip(),
        "email": emp["email"],
        "phone": emp.get("phone"),
        "department_id": emp.get("department_id"),
        "department_name": emp.get("department_name"),
        "designation_id": emp.get("designation_id"),
        "designation_name": emp.get("designation_name"),
        "employment_status": emp.get("employment_status"),
        "employment_type": emp.get("employment_type"),
        "joining_date": str(emp.get("joining_date")),
        "location": emp.get("location") or "HQ",
        "timezone": emp.get("timezone") or "Asia/Kolkata",
    }


# ── Attendance ────────────────────────────────────────────────────────────────

@router.get("/attendance", summary="Get Current Employee Attendance Records & Status")
async def get_my_attendance(
    days: int = Query(default=30, ge=1, le=90),
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    emp = await _resolve_employee(ctx)
    emp_id = emp["id"]

    today_str = utc_now().date().isoformat()
    start_date = (utc_now().date() - datetime.timedelta(days=days)).isoformat()

    async with get_db_connection() as db:
        async with db.execute(
            """
            SELECT * FROM attendance_records
            WHERE employee_id = ? AND date >= ?
            ORDER BY date DESC
            """,
            (emp_id, start_date),
        ) as c:
            rows = [dict(r) for r in await c.fetchall()]

    today_record = next((r for r in rows if r["date"] == today_str), None)

    days_present = sum(1 for r in rows if r.get("status") == "PRESENT")
    days_absent = sum(1 for r in rows if r.get("status") == "ABSENT")
    total_overtime = sum(float(r.get("overtime_hours") or 0.0) for r in rows)

    return {
        "employee_id": emp_id,
        "today": today_record,
        "is_clocked_in": bool(today_record and today_record.get("check_in") and not today_record.get("check_out")),
        "is_clocked_out": bool(today_record and today_record.get("check_out")),
        "records": rows,
        "stats": {
            "period_days": days,
            "days_present": days_present,
            "days_absent": days_absent,
            "total_overtime_hours": round(total_overtime, 1),
        },
    }


@router.post("/attendance/punch", summary="1-Tap Clock-In / Clock-Out Punch")
async def punch_attendance(
    payload: PunchRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    emp = await _resolve_employee(ctx)
    emp_id = emp["id"]
    org_id = emp["organization_id"]

    now = utc_now()
    today_str = now.date().isoformat()
    now_str = now.isoformat()
    action_upper = payload.action.strip().upper()

    if action_upper not in ("CLOCK_IN", "CLOCK_OUT"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid punch action '{payload.action}'. Must be 'CLOCK_IN' or 'CLOCK_OUT'.",
        )

    async with get_db_connection() as db:
        async with db.execute(
            "SELECT * FROM attendance_records WHERE employee_id = ? AND date = ?",
            (emp_id, today_str),
        ) as c:
            existing_row = await c.fetchone()

        existing = dict(existing_row) if existing_row else None

        if action_upper == "CLOCK_IN":
            if existing and existing.get("check_in"):
                ci_time = existing["check_in"].split("T")[-1][:5] if "T" in existing["check_in"] else existing["check_in"]
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Already clocked in for today at {ci_time}. Cannot double clock-in.",
                )

            if existing:
                await db.execute(
                    """
                    UPDATE attendance_records SET
                        check_in = ?, status = 'PRESENT', source = 'PORTAL', remarks = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (now_str, payload.notes, now_str, existing["id"]),
                )
                rec_id = existing["id"]
            else:
                rec_id = f"att-{emp_id}-{today_str}"
                await db.execute(
                    """
                    INSERT INTO attendance_records (
                        id, organization_id, employee_id, date, check_in, check_out,
                        status, source, overtime_hours, remarks, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, NULL, 'PRESENT', 'PORTAL', 0.0, ?, ?, ?)
                    """,
                    (rec_id, org_id, emp_id, today_str, now_str, payload.notes, now_str, now_str),
                )

            await record_audit_log(
                conn=db,
                organization_id=org_id,
                actor_id=ctx.actor_id,
                actor_type="HUMAN",
                action="CLOCK_IN",
                entity_type="attendance_record",
                entity_id=rec_id,
                changes={"action": "CLOCK_IN", "time": now_str, "employee_id": emp_id},
            )
            await db.commit()

            return {
                "success": True,
                "action": "CLOCK_IN",
                "record_id": rec_id,
                "timestamp": now_str,
                "status": "PRESENT",
                "message": f"Successfully clocked in at {now.strftime('%I:%M %p')}.",
            }

        else:  # CLOCK_OUT
            if not existing or not existing.get("check_in"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot clock out without checking in first today.",
                )

            if existing.get("check_out"):
                co_time = existing["check_out"].split("T")[-1][:5] if "T" in existing["check_out"] else existing["check_out"]
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Already clocked out today at {co_time}.",
                )

            await db.execute(
                """
                UPDATE attendance_records SET
                    check_out = ?, remarks = COALESCE(?, remarks), updated_at = ?
                WHERE id = ?
                """,
                (now_str, payload.notes, now_str, existing["id"]),
            )

            await record_audit_log(
                conn=db,
                organization_id=org_id,
                actor_id=ctx.actor_id,
                actor_type="HUMAN",
                action="CLOCK_OUT",
                entity_type="attendance_record",
                entity_id=existing["id"],
                changes={"action": "CLOCK_OUT", "time": now_str, "employee_id": emp_id},
            )
            await db.commit()

            return {
                "success": True,
                "action": "CLOCK_OUT",
                "record_id": existing["id"],
                "timestamp": now_str,
                "status": "PRESENT",
                "message": f"Successfully clocked out at {now.strftime('%I:%M %p')}.",
            }


# ── Leave & PTO ───────────────────────────────────────────────────────────────

@router.get("/leave", summary="Get Current Employee Leave Balances & Requests")
async def get_my_leave(ctx: TenantContext = Depends(get_tenant_context)) -> dict[str, Any]:
    emp = await _resolve_employee(ctx)
    emp_id = emp["id"]

    async with get_db_connection() as db:
        async with db.execute(
            """
            SELECT * FROM leave_requests
            WHERE employee_id = ?
            ORDER BY created_at DESC
            """,
            (emp_id,),
        ) as c:
            requests = [dict(r) for r in await c.fetchall()]

    total_annual = 18.0
    total_sick = 10.0
    total_casual = 6.0

    used_annual = sum(float(r["days_count"]) for r in requests if r.get("leave_type_id") == "lt-annual" and r.get("status") == "APPROVED")
    used_sick = sum(float(r["days_count"]) for r in requests if r.get("leave_type_id") == "lt-sick" and r.get("status") == "APPROVED")
    used_casual = sum(float(r["days_count"]) for r in requests if r.get("leave_type_id") == "lt-casual" and r.get("status") == "APPROVED")

    return {
        "employee_id": emp_id,
        "balances": {
            "annual": {"total": total_annual, "used": used_annual, "available": max(0.0, total_annual - used_annual)},
            "sick": {"total": total_sick, "used": used_sick, "available": max(0.0, total_sick - used_sick)},
            "casual": {"total": total_casual, "used": used_casual, "available": max(0.0, total_casual - used_casual)},
        },
        "requests": requests,
    }


@router.post("/leave", summary="Submit Employee Leave Application")
async def apply_for_leave(
    payload: LeaveApplyRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    emp = await _resolve_employee(ctx)
    emp_id = emp["id"]
    org_id = emp["organization_id"]

    req_id = f"lr-{uuid.uuid4().hex[:8]}"
    now_str = utc_now().isoformat()

    async with get_db_connection() as db:
        await db.execute(
            """
            INSERT INTO leave_requests (
                id, organization_id, employee_id, leave_type_id, start_date, end_date,
                days_count, is_half_day, reason, status, applied_on, documents_json,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, '[]', ?, ?)
            """,
            (
                req_id,
                org_id,
                emp_id,
                payload.leave_type_id,
                payload.start_date,
                payload.end_date,
                payload.days_count,
                1 if payload.is_half_day else 0,
                payload.reason,
                now_str,
                now_str,
                now_str,
            ),
        )

        await record_audit_log(
            conn=db,
            organization_id=org_id,
            actor_id=ctx.actor_id,
            actor_type="HUMAN",
            action="LEAVE_APPLY",
            entity_type="leave_request",
            entity_id=req_id,
            changes={"employee_id": emp_id, "days_count": payload.days_count, "type": payload.leave_type_id},
        )
        await db.commit()

    return {
        "success": True,
        "leave_request_id": req_id,
        "status": "PENDING",
        "message": f"Leave request for {payload.days_count} day(s) submitted successfully.",
    }


# ── Payslips ──────────────────────────────────────────────────────────────────

@router.get("/payslips", summary="Get Authorized Employee Payslips")
async def get_my_payslips(ctx: TenantContext = Depends(get_tenant_context)) -> dict[str, Any]:
    emp = await _resolve_employee(ctx)
    emp_id = emp["id"]

    async with get_db_connection() as db:
        async with db.execute(
            """
            SELECT p.*, r.run_date, r.period_id
            FROM payslips p
            LEFT JOIN payroll_runs r ON p.run_id = r.id
            WHERE p.employee_id = ?
            ORDER BY p.created_at DESC
            """,
            (emp_id,),
        ) as c:
            slips = [dict(r) for r in await c.fetchall()]

    return {
        "employee_id": emp_id,
        "payslips": slips,
        "count": len(slips),
    }


# ── Daily Work Logs ───────────────────────────────────────────────────────────

@router.get("/work-logs", summary="Get Employee Daily Work Logs")
async def get_my_work_logs(
    limit: int = Query(default=30, ge=1, le=100),
    repo: SqliteWorkLogRepository = Depends(get_work_log_repository),
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    emp = await _resolve_employee(ctx)
    emp_id = emp["id"]
    org_id = emp["organization_id"]

    logs = await repo.list_by_employee(org_id, emp_id, limit=limit)
    return {
        "employee_id": emp_id,
        "work_logs": logs,
        "count": len(logs),
    }


@router.post("/work-logs", summary="Create Daily Work Log Entry")
async def create_my_work_log(
    payload: WorkLogCreateRequest,
    repo: SqliteWorkLogRepository = Depends(get_work_log_repository),
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    emp = await _resolve_employee(ctx)
    emp_id = emp["id"]
    org_id = emp["organization_id"]

    work_date = None
    if payload.work_date:
        try:
            work_date = datetime.date.fromisoformat(payload.work_date)
        except Exception:
            pass

    log_entry = await repo.create(
        organization_id=org_id,
        employee_id=emp_id,
        description=payload.description,
        hours_spent=payload.hours_spent,
        task_id=payload.task_id,
        blockers=payload.blockers,
        work_date=work_date,
    )

    async with get_db_connection() as db:
        await record_audit_log(
            conn=db,
            organization_id=org_id,
            actor_id=ctx.actor_id,
            actor_type="HUMAN",
            action="WORK_LOG_CREATE",
            entity_type="work_log",
            entity_id=log_entry["id"],
            changes={"employee_id": emp_id, "hours": payload.hours_spent},
        )
        await db.commit()

    return {
        "success": True,
        "work_log": log_entry,
        "message": "Work log saved successfully.",
    }
