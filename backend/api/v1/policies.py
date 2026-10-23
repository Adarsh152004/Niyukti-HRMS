"""
API v1 — HR Policy Endpoints (`/api/v1/policies`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_policy_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.policy_service import HRPolicyService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.policy import PolicyCategory

router = APIRouter(prefix="/api/v1/policies", tags=["Policies"])


class CreatePolicyRequest(BaseModel):
    title: str
    content: str
    category: PolicyCategory = PolicyCategory.CODE_OF_CONDUCT
    version: str = "1.0"


@router.post("", summary="Create HR Policy")
async def create_policy(
    req: CreatePolicyRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[HRPolicyService, Depends(get_policy_service)],
) -> JSONResponse:
    policy = await service.create_policy(
        organization_id=ctx.organization_id,
        title=req.title,
        content=req.content,
        category=req.category,
        version=req.version,
    )
    return success_response(data=policy.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/{policy_id}", summary="Get HR Policy")
async def get_policy(
    policy_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[HRPolicyService, Depends(get_policy_service)],
) -> JSONResponse:
    policy = await service.get_policy(ctx.organization_id, policy_id)
    if not policy:
        return error_response(code="POLICY_NOT_FOUND", message="Policy not found", status_code=404)
    return success_response(data=policy.model_dump())


@router.get("", summary="List HR Policies")
async def list_policies(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[HRPolicyService, Depends(get_policy_service)],
) -> JSONResponse:
    policies = await service.list_policies(ctx.organization_id)
    return success_response(data=[p.model_dump() for p in policies])
