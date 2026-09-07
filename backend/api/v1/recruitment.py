"""
API v1 — Recruitment Endpoints (`/api/v1/recruitment`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_recruitment_service, get_tenant_context
from backend.api.response import success_response
from backend.hrms.application.recruitment_service import RecruitmentService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.recruitment import CandidateSource

router = APIRouter(prefix="/api/v1/recruitment", tags=["Recruitment"])


class CreateRequisitionRequest(BaseModel):
    title: str
    department_id: str
    headcount: int = 1
    job_description: str = ""
    min_salary: float | None = None
    max_salary: float | None = None


class AddCandidateRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    source: CandidateSource = CandidateSource.DIRECT_APPLY
    phone: str | None = None
    years_of_experience: float | None = None


@router.post("/requisitions", summary="Create Job Requisition")
async def create_requisition(
    req: CreateRequisitionRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[RecruitmentService, Depends(get_recruitment_service)],
) -> JSONResponse:
    requisition = await service.create_requisition(
        organization_id=ctx.organization_id,
        title=req.title,
        department_id=req.department_id,
        headcount=req.headcount,
        job_description=req.job_description,
        min_salary=req.min_salary,
        max_salary=req.max_salary,
    )
    return success_response(data=requisition.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/requisitions", summary="List Job Requisitions")
async def list_requisitions(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[RecruitmentService, Depends(get_recruitment_service)],
) -> JSONResponse:
    reqs = await service.list_requisitions(ctx.organization_id)
    return success_response(data=[r.model_dump() for r in reqs])


@router.post("/candidates", summary="Add Candidate")
async def add_candidate(
    req: AddCandidateRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[RecruitmentService, Depends(get_recruitment_service)],
) -> JSONResponse:
    cand = await service.add_candidate(
        organization_id=ctx.organization_id,
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        source=req.source,
        phone=req.phone,
        years_of_experience=req.years_of_experience,
    )
    return success_response(data=cand.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/candidates", summary="List Candidates")
async def list_candidates(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[RecruitmentService, Depends(get_recruitment_service)],
) -> JSONResponse:
    cands = await service.list_candidates(ctx.organization_id)
    return success_response(data=[c.model_dump() for c in cands])
