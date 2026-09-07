"""
API v1 — Approval Inbox Endpoints (`/api/v1/approvals`).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_approval_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.approval_service import ApprovalInboxService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.approvals import ApprovalType

router = APIRouter(prefix="/api/v1/approvals", tags=["Approvals"])


class SubmitApprovalRequest(BaseModel):
    approval_type: ApprovalType
    target_entity_id: str
    payload: dict[str, Any] | None = None
    risk_level: str = "MEDIUM"


class DecideApprovalRequest(BaseModel):
    decision: str
    rejection_reason: str | None = None


@router.post("", summary="Submit Approval Request")
async def submit_approval(
    req: SubmitApprovalRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ApprovalInboxService, Depends(get_approval_service)],
) -> JSONResponse:
    request = await service.submit_request(
        organization_id=ctx.organization_id,
        approval_type=req.approval_type,
        requester_id=ctx.actor_id,
        requester_role=ctx.actor_type.value,
        target_entity_id=req.target_entity_id,
        payload=req.payload,
        risk_level=req.risk_level,
    )
    return success_response(data=request.model_dump(), status_code=status.HTTP_201_CREATED)


@router.post("/{approval_id}/decide", summary="Decide on Approval Request")
async def decide_approval(
    approval_id: str,
    req: DecideApprovalRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ApprovalInboxService, Depends(get_approval_service)],
) -> JSONResponse:
    res = await service.decide_request(
        organization_id=ctx.organization_id,
        approval_id=approval_id,
        approver_id=ctx.actor_id,
        approver_role=ctx.actor_type.value,
        decision=req.decision,
        rejection_reason=req.rejection_reason,
    )
    if not res:
        return error_response(code="APPROVAL_NOT_FOUND", message="Pending approval request not found", status_code=404)
    return success_response(data=res.model_dump())


@router.get("/pending", summary="List Pending Approvals")
async def list_pending(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ApprovalInboxService, Depends(get_approval_service)],
) -> JSONResponse:
    pending = await service.list_pending(ctx.organization_id)
    return success_response(data=[p.model_dump() for p in pending])
