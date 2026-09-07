"""
API v1 — Learning LMS Endpoints (`/api/v1/learning`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_learning_service, get_tenant_context
from backend.api.response import success_response
from backend.hrms.application.learning_service import LearningService
from backend.hrms.application.tenant_context import TenantContext

router = APIRouter(prefix="/api/v1/learning", tags=["Learning"])


class CreateCourseRequest(BaseModel):
    title: str
    duration_hours: float
    description: str = ""
    category: str = "TECHNICAL"


class EnrollCourseRequest(BaseModel):
    course_id: str
    employee_id: str


@router.post("/courses", summary="Create Course")
async def create_course(
    req: CreateCourseRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[LearningService, Depends(get_learning_service)],
) -> JSONResponse:
    course = await service.create_course(
        organization_id=ctx.organization_id,
        title=req.title,
        duration_hours=req.duration_hours,
        description=req.description,
        category=req.category,
    )
    return success_response(data=course.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/courses", summary="List Courses")
async def list_courses(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[LearningService, Depends(get_learning_service)],
) -> JSONResponse:
    courses = await service.list_courses(ctx.organization_id)
    return success_response(data=[c.model_dump() for c in courses])


@router.post("/enrollments", summary="Enroll Employee in Course")
async def enroll_course(
    req: EnrollCourseRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[LearningService, Depends(get_learning_service)],
) -> JSONResponse:
    enrollment = await service.enroll_employee(
        organization_id=ctx.organization_id,
        course_id=req.course_id,
        employee_id=req.employee_id,
    )
    return success_response(data=enrollment.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/enrollments/employee/{employee_id}", summary="List Employee Enrollments")
async def list_enrollments(
    employee_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[LearningService, Depends(get_learning_service)],
) -> JSONResponse:
    enrollments = await service.list_enrollments(ctx.organization_id, employee_id)
    return success_response(data=[e.model_dump() for e in enrollments])
