"""
API v1 — Leave Endpoints (`/api/v1/leaves` & `/api/v1/leave`).
Strict SQLite persistence, flexible leave type parsing, and robust error handling.
"""

from __future__ import annotations

import datetime
from datetime import date
import uuid
import logging
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.api.dependencies import get_leave_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.database.sqlite_db import get_db_connection, record_audit_log
from backend.hrms.application.leave_service import LeaveService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.common import LeaveType, utc_now

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/leaves", tags=["Leaves"])
alias_router = APIRouter(prefix="/api/v1/leave", tags=["Leaves (Alias)"])


def normalize_leave_type(val: Any) -> str:
    """Safely normalizes any leave type representation to a standard leave_type_id."""
    if not val:
        return "lt-annual"
    s = str(val).lower().replace("leavetype.", "").strip()
    if "sick" in s:
        return "lt-sick"
    if "casual" in s:
        return "lt-casual"
    if "matern" in s:
        return "lt-maternity"
    if "patern" in s:
        return "lt-paternity"
    if "unpaid" in s or "loss" in s:
        return "lt-unpaid"
    return "lt-annual"


def to_domain_leave_type(val: Any) -> LeaveType:
    norm = normalize_leave_type(val)
    if norm == "lt-sick":
        return LeaveType.SICK
    if norm == "lt-casual":
        return LeaveType.CASUAL
    if norm == "lt-maternity":
        return LeaveType.MATERNITY
    return LeaveType.ANNUAL


# ── Schemas ───────────────────────────────────────────────────────────────────

class LeaveDecisionRequest(BaseModel):
    status: str
    remarks: Optional[str] = None


class ApplyLeaveRequest(BaseModel):
    employee_id: str
    leave_type: Any = Field(default="lt-annual", description="e.g. 'lt-annual', 'ANNUAL', 'lt-sick'")
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    reason: Optional[str] = Field(default="Personal leave / PTO")
    days_count: Optional[float] = None
    is_half_day: bool = False


# ── Handlers ──────────────────────────────────────────────────────────────────

@router.get("", summary="List All Organization Leave Requests")
async def list_all_leaves(
    status_filter: str | None = None,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)] = None,
) -> JSONResponse:
    async with get_db_connection() as db:
        query = """
        SELECT 
            lr.id,
            lr.organization_id,
            lr.employee_id,
            lr.leave_type_id,
            lr.start_date,
            lr.end_date,
            lr.days_count,
            lr.is_half_day,
            lr.reason,
            lr.status,
            lr.applied_on,
            lr.approved_by,
            lr.approved_on,
            lr.created_at,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.email,
            d.name as department_name
        FROM leave_requests lr
        LEFT JOIN employees e ON lr.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        """
        params = []
        if status_filter:
            query += " WHERE UPPER(lr.status) = ?"
            params.append(status_filter.upper())
        query += " ORDER BY lr.created_at DESC LIMIT 150"

        async with db.execute(query, tuple(params)) as c:
            rows = [dict(r) for r in await c.fetchall()]

    return success_response(data=rows)


@router.post("/apply", summary="Apply for Leave")
async def apply_leave(
    req: ApplyLeaveRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)] = None,
    service: Annotated[LeaveService, Depends(get_leave_service)] = None,
) -> JSONResponse:
    org_id = ctx.organization_id if ctx else "org-nova-01"
    actor_id = ctx.actor_id if ctx else req.employee_id

    # Parse and compute days count
    start_str = str(req.start_date).split("T")[0]
    end_str = str(req.end_date).split("T")[0]

    try:
        sd = datetime.date.fromisoformat(start_str)
        ed = datetime.date.fromisoformat(end_str)
        diff_days = max(1.0, float((ed - sd).days + 1))
    except Exception:
        sd = datetime.date.today()
        ed = datetime.date.today()
        diff_days = 1.0

    days_count = 0.5 if req.is_half_day else (req.days_count or diff_days)
    leave_type_id = normalize_leave_type(req.leave_type)
    reason_clean = (req.reason or "").strip() or "Personal leave / PTO"

    req_id = f"lr-{uuid.uuid4().hex[:8]}"
    now_str = utc_now().isoformat()

    # 1. Direct SQLite Core Persistence
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
                req.employee_id,
                leave_type_id,
                start_str,
                end_str,
                days_count,
                1 if req.is_half_day else 0,
                reason_clean,
                now_str,
                now_str,
                now_str,
            ),
        )

        await record_audit_log(
            conn=db,
            organization_id=org_id,
            actor_id=actor_id,
            actor_type="HUMAN",
            action="LEAVE_APPLY",
            entity_type="leave_request",
            entity_id=req_id,
            changes={"employee_id": req.employee_id, "days_count": days_count, "type": leave_type_id},
        )
        await db.commit()

    # 2. Also register with in-memory service if available
    if service:
        try:
            d_type = to_domain_leave_type(req.leave_type)
            await service.apply_leave(
                organization_id=org_id,
                employee_id=req.employee_id,
                leave_type=d_type,
                start_date=sd,
                end_date=ed,
                reason=reason_clean,
                is_half_day=req.is_half_day,
            )
        except Exception as e:
            logger.info(f"Service registration note: {e}")

    logger.info(f"✅ Leave application persisted to SQLite: {req_id} for {req.employee_id} ({days_count} days)")

    return success_response(
        data={
            "id": req_id,
            "leave_request_id": req_id,
            "organization_id": org_id,
            "employee_id": req.employee_id,
            "leave_type_id": leave_type_id,
            "start_date": start_str,
            "end_date": end_str,
            "days_count": days_count,
            "is_half_day": req.is_half_day,
            "reason": reason_clean,
            "status": "PENDING",
            "applied_on": now_str,
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/{leave_id}/decision", summary="Approve or Reject Leave")
async def decide_leave(
    leave_id: str,
    req: LeaveDecisionRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)] = None,
) -> JSONResponse:
    new_status = req.status.upper()
    now_str = utc_now().isoformat()
    actor = ctx.actor_id if ctx else "hr-manager"

    async with get_db_connection() as db:
        await db.execute(
            """
            UPDATE leave_requests SET
                status = ?,
                approved_by = ?,
                approved_on = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (new_status, actor, now_str, now_str, leave_id),
        )
        await db.commit()

    return success_response(data={"id": leave_id, "status": new_status})


@router.post("/{leave_id}/approve", summary="Approve Leave")
async def approve_leave(
    leave_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)] = None,
    service: Annotated[LeaveService, Depends(get_leave_service)] = None,
) -> JSONResponse:
    now_str = utc_now().isoformat()
    actor = ctx.actor_id if ctx else "hr-manager"

    async with get_db_connection() as db:
        await db.execute(
            """
            UPDATE leave_requests SET
                status = 'APPROVED',
                approved_by = ?,
                approved_on = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (actor, now_str, now_str, leave_id),
        )
        await db.commit()

    return success_response(data={"id": leave_id, "status": "APPROVED"})


@router.post("/{leave_id}/reject", summary="Reject Leave")
async def reject_leave(
    leave_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)] = None,
) -> JSONResponse:
    now_str = utc_now().isoformat()
    actor = ctx.actor_id if ctx else "hr-manager"

    async with get_db_connection() as db:
        await db.execute(
            """
            UPDATE leave_requests SET
                status = 'REJECTED',
                approved_by = ?,
                approved_on = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (actor, now_str, now_str, leave_id),
        )
        await db.commit()

    return success_response(data={"id": leave_id, "status": "REJECTED"})


@router.get("/employee/{employee_id}", summary="List Employee Leaves")
async def list_leaves(
    employee_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)] = None,
) -> JSONResponse:
    async with get_db_connection() as db:
        async with db.execute(
            "SELECT * FROM leave_requests WHERE employee_id = ? ORDER BY created_at DESC",
            (employee_id,),
        ) as c:
            rows = [dict(r) for r in await c.fetchall()]

    return success_response(data=rows)


# ── Attach alias endpoints to alias_router ────────────────────────────────────
alias_router.add_api_route("", list_all_leaves, methods=["GET"])
alias_router.add_api_route("/apply", apply_leave, methods=["POST"], status_code=status.HTTP_201_CREATED)
alias_router.add_api_route("/{leave_id}/decision", decide_leave, methods=["POST"])
alias_router.add_api_route("/{leave_id}/approve", approve_leave, methods=["POST"])
alias_router.add_api_route("/{leave_id}/reject", reject_leave, methods=["POST"])
alias_router.add_api_route("/employee/{employee_id}", list_leaves, methods=["GET"])
