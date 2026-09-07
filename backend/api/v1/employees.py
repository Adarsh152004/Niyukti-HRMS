"""
API v1 — Employee Endpoints (`/api/v1/employees`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_employee_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.services import EmployeeService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.employee import EmploymentStatus, EmploymentType
from backend.hrms.domain.exceptions import HRMSException

router = APIRouter(prefix="/api/v1/employees", tags=["Employees"])


class CreateEmployeeRequest(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    email: str
    department_id: str
    designation_id: str
    joining_date: str
    preferred_name: str | None = None
    phone: str | None = None
    manager_id: str | None = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    location: str | None = None
    timezone: str = "Asia/Kolkata"


class UpdateEmployeeStatusRequest(BaseModel):
    status: EmploymentStatus


@router.post("", summary="Create Employee")
async def create_employee(
    req: CreateEmployeeRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> JSONResponse:
    try:
        emp = await service.create_employee(
            ctx=ctx,
            employee_code=req.employee_code,
            first_name=req.first_name,
            last_name=req.last_name,
            email=req.email,
            department_id=req.department_id,
            designation_id=req.designation_id,
            joining_date=req.joining_date,
            preferred_name=req.preferred_name,
            phone=req.phone,
            manager_id=req.manager_id,
            employment_type=req.employment_type,
            location=req.location,
            timezone=req.timezone,
        )
        return success_response(data=emp.model_dump(), status_code=status.HTTP_201_CREATED)
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)


@router.get("", summary="List Employees")
async def list_employees(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    department_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> JSONResponse:
    try:
        emps = await service.list_employees(ctx, department_id, limit, offset)
        return success_response(data=[e.model_dump() for e in emps])
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)


@router.get("/{employee_id}", summary="Get Employee by ID")
async def get_employee(
    employee_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> JSONResponse:
    try:
        emp = await service.get_employee(ctx, employee_id)
        return success_response(data=emp.model_dump())
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=404 if e.code == "EMPLOYEE_NOT_FOUND" else 400)


@router.patch("/{employee_id}/status", summary="Update Employee Employment Status")
async def update_employee_status(
    employee_id: str,
    req: UpdateEmployeeStatusRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> JSONResponse:
    try:
        emp = await service.update_employee_status(ctx, employee_id, req.status)
        return success_response(data=emp.model_dump())
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)
