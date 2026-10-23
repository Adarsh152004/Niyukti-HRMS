"""
API v1 — Attendance Endpoints (`/api/v1/attendance`).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_attendance_service, get_tenant_context
from backend.api.response import success_response
from backend.database.sqlite_db import get_db_connection
from backend.hrms.application.attendance_service import AttendanceService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.common import utc_now

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance"])


@router.get("", summary="Get Today's Organization Attendance Records")
async def get_organization_attendance(
    record_date: date | None = None,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)] = None,
) -> JSONResponse:
    target_date = (record_date or utc_now().date()).isoformat()
    async with get_db_connection() as db:
        query = """
        SELECT 
            e.id as employee_id,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.email,
            e.location,
            d.name as department_name,
            des.name as designation_title,
            ar.id as attendance_id,
            ar.date as record_date,
            ar.check_in,
            ar.check_out,
            ar.status,
            ar.source,
            ar.overtime_hours,
            ar.remarks
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN designations des ON e.designation_id = des.id
        LEFT JOIN attendance_records ar ON e.id = ar.employee_id AND ar.date = ?
        WHERE e.employment_status = 'ACTIVE'
        ORDER BY e.employee_code ASC
        """
        async with db.execute(query, (target_date,)) as c:
            rows = [dict(r) for r in await c.fetchall()]

    return success_response(data=rows)


class CheckInRequest(BaseModel):
    employee_id: str
    record_date: date
    check_in_time: datetime | None = None


class CheckOutRequest(BaseModel):
    employee_id: str
    record_date: date
    check_out_time: datetime | None = None


@router.post("/check-in", summary="Log Check-In")
async def check_in(
    req: CheckInRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> JSONResponse:
    rec = await service.log_check_in(ctx.organization_id, req.employee_id, req.record_date, req.check_in_time)
    return success_response(data=rec.model_dump(), status_code=status.HTTP_200_OK)


@router.post("/check-out", summary="Log Check-Out")
async def check_out(
    req: CheckOutRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> JSONResponse:
    rec = await service.log_check_out(ctx.organization_id, req.employee_id, req.record_date, req.check_out_time)
    return success_response(data=rec.model_dump(), status_code=status.HTTP_200_OK)


@router.get("/employee/{employee_id}", summary="Get Employee Attendance Records")
async def get_attendance(
    employee_id: str,
    start_date: date,
    end_date: date,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[AttendanceService, Depends(get_attendance_service)],
) -> JSONResponse:
    records = await service.get_records(ctx.organization_id, employee_id, start_date, end_date)
    return success_response(data=[r.model_dump() for r in records])
