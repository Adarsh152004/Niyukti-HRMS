"""
API v1 — Skill Endpoints (`/api/v1/skills`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_skill_service, get_tenant_context
from backend.api.response import error_response, success_response
from backend.hrms.application.services import SkillService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.exceptions import HRMSException
from backend.hrms.domain.skills import Proficiency, SkillCategory

router = APIRouter(prefix="/api/v1/skills", tags=["Skills"])


class CreateSkillRequest(BaseModel):
    name: str
    category: SkillCategory = SkillCategory.TECHNICAL
    description: str | None = None


class AddEmployeeSkillRequest(BaseModel):
    employee_id: str
    skill_id: str
    proficiency: Proficiency = Proficiency.INTERMEDIATE
    years_experience: float = 0.0


@router.post("", summary="Create Skill Catalog Entry")
async def create_skill(
    req: CreateSkillRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[SkillService, Depends(get_skill_service)],
) -> JSONResponse:
    try:
        skill = await service.create_skill(
            ctx=ctx,
            name=req.name,
            category=req.category,
            description=req.description,
        )
        return success_response(data=skill.model_dump(), status_code=status.HTTP_201_CREATED)
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)


@router.post("/employee", summary="Add Skill to Employee Profile")
async def add_employee_skill(
    req: AddEmployeeSkillRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[SkillService, Depends(get_skill_service)],
) -> JSONResponse:
    try:
        emp_skill = await service.add_employee_skill(
            ctx=ctx,
            employee_id=req.employee_id,
            skill_id=req.skill_id,
            proficiency=req.proficiency,
            years_experience=req.years_experience,
        )
        return success_response(data=emp_skill.model_dump(), status_code=status.HTTP_201_CREATED)
    except HRMSException as e:
        return error_response(code=e.code, message=e.message, status_code=400)
