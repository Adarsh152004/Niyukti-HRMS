"""
API v1 — Organization Endpoints (`/api/v1/organizations`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_organization_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.services import OrganizationService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.exceptions import HRMSException

router = APIRouter(prefix="/api/v1/organizations", tags=["Organizations"])


class CreateOrganizationRequest(BaseModel):
    legal_name: str
    display_name: str
    slug: str
    industry: str | None = None
    country: str = "IN"
    timezone: str = "Asia/Kolkata"
    currency: str = "INR"


@router.post("", summary="Create a new Organization/Tenant")
async def create_organization(
    req: CreateOrganizationRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> JSONResponse:
    try:
        org = await service.create_organization(
            ctx=ctx,
            legal_name=req.legal_name,
            display_name=req.display_name,
            slug=req.slug,
            industry=req.industry,
            country=req.country,
            timezone=req.timezone,
            currency=req.currency,
        )
        return success_response(data=org.model_dump(), status_code=status.HTTP_201_CREATED)
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)


@router.get("/{organization_id}", summary="Get Organization by ID")
async def get_organization(
    organization_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[OrganizationService, Depends(get_organization_service)],
) -> JSONResponse:
    try:
        org = await service.get_organization(ctx, organization_id)
        return success_response(data=org.model_dump())
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=404)
