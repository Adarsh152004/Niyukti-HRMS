"""
API v1 — Leave Endpoints (`/api/v1/leaves`).
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_leave_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.database.sqlite_db import get_db_connection
from backend.hrms.application.leave_service import LeaveService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.common import LeaveType, utc_now

router = APIRouter(prefix="/api/v1/leaves", tags=["Leaves"])


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
        query += " ORDER BY lr.created_at DESC LIMIT 100"

        async with db.execute(query, tuple(params)) as c:
            rows = [dict(r) for r in await c.fetchall()]

    return success_response(data=rows)


class LeaveDecisionRequest(BaseModel):
    status: str
    remarks: str | None = None


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


class ApplyLeaveRequest(BaseModel):
    employee_id: str
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str | None = None
    is_half_day: bool = False


@router.post("/apply", summary="Apply for Leave")
async def apply_leave(
    req: ApplyLeaveRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[LeaveService, Depends(get_leave_service)],
) -> JSONResponse:
    leave = await service.apply_leave(
        organization_id=ctx.organization_id,
        employee_id=req.employee_id,
        leave_type=req.leave_type,
        start_date=req.start_date,
        end_date=req.end_date,
        reason=req.reason,
        is_half_day=req.is_half_day,
    )
    return success_response(data=leave.model_dump(), status_code=status.HTTP_201_CREATED)


@router.post("/{leave_id}/approve", summary="Approve Leave")
async def approve_leave(
    leave_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[LeaveService, Depends(get_leave_service)],
) -> JSONResponse:
    res = await service.approve_leave(ctx.organization_id, leave_id, ctx.actor_id)
    if not res:
        return error_response(code="LEAVE_NOT_FOUND", message="Pending leave request not found", status_code=404)
    return success_response(data=res.model_dump())


@router.get("/employee/{employee_id}", summary="List Employee Leaves")
async def list_leaves(
    employee_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[LeaveService, Depends(get_leave_service)],
) -> JSONResponse:
    leaves = await service.list_employee_leaves(ctx.organization_id, employee_id)
    return success_response(data=[lv.model_dump() for lv in leaves])
