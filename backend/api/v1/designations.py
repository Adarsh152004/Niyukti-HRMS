"""
API v1 — Designation Endpoints (`/api/v1/designations`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_designation_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.services import DesignationService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.exceptions import HRMSException

router = APIRouter(prefix="/api/v1/designations", tags=["Designations"])


class CreateDesignationRequest(BaseModel):
    name: str
    code: str
    description: str | None = None
    level: int = 1
    department_id: str | None = None


@router.post("", summary="Create Designation")
async def create_designation(
    req: CreateDesignationRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[DesignationService, Depends(get_designation_service)],
) -> JSONResponse:
    try:
        des = await service.create_designation(
            ctx=ctx,
            name=req.name,
            code=req.code,
            description=req.description,
            level=req.level,
            department_id=req.department_id,
        )
        return success_response(data=des.model_dump(), status_code=status.HTTP_201_CREATED)
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)


@router.get("", summary="List Designations")
async def list_designations(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[DesignationService, Depends(get_designation_service)],
) -> JSONResponse:
    try:
        dess = await service.list_designations(ctx)
        return success_response(data=[d.model_dump() for d in dess])
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)
