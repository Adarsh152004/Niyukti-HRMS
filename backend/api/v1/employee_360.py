"""
API v1 — Employee 360 Consolidated Endpoints (`/api/v1/employees/{id}/360`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.api.dependencies import get_employee_360_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.employee_360_service import Employee360Service
from backend.hrms.application.tenant_context import TenantContext

router = APIRouter(prefix="/api/v1/employees", tags=["Employee 360"])


@router.get("/{employee_id}/360", summary="Get Unified Employee 360 Profile")
async def get_employee_360(
    employee_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[Employee360Service, Depends(get_employee_360_service)],
) -> JSONResponse:
    profile = await service.get_employee_360(ctx.organization_id, employee_id)
    if not profile:
        return error_response(code="EMPLOYEE_NOT_FOUND", message=f"Employee [{employee_id}] not found in tenant", status_code=404)
    return success_response(data=profile.model_dump())
