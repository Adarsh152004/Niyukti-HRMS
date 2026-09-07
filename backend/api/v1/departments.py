"""
API v1 — Department Endpoints (`/api/v1/departments`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_department_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.services import DepartmentService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.exceptions import HRMSException

router = APIRouter(prefix="/api/v1/departments", tags=["Departments"])


class CreateDepartmentRequest(BaseModel):
    name: str
    code: str
    description: str | None = None
    manager_employee_id: str | None = None
    parent_department_id: str | None = None


@router.post("", summary="Create Department")
async def create_department(
    req: CreateDepartmentRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[DepartmentService, Depends(get_department_service)],
) -> JSONResponse:
    try:
        dept = await service.create_department(
            ctx=ctx,
            name=req.name,
            code=req.code,
            description=req.description,
            manager_employee_id=req.manager_employee_id,
            parent_department_id=req.parent_department_id,
        )
        return success_response(data=dept.model_dump(), status_code=status.HTTP_201_CREATED)
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)


@router.get("", summary="List Departments")
async def list_departments(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[DepartmentService, Depends(get_department_service)],
) -> JSONResponse:
    try:
        depts = await service.list_departments(ctx)
        return success_response(data=[d.model_dump() for d in depts])
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)
