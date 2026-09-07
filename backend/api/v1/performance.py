"""
API v1 — Performance Endpoints (`/api/v1/performance`).
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_performance_service, get_tenant_context
from backend.api.response import success_response
from backend.hrms.application.performance_service import PerformanceService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.performance import GoalCategory

router = APIRouter(prefix="/api/v1/performance", tags=["Performance"])


class CreateCycleRequest(BaseModel):
    name: str
    start_date: date
    end_date: date
    description: str = ""


class CreateGoalRequest(BaseModel):
    employee_id: str
    title: str
    category: GoalCategory = GoalCategory.INDIVIDUAL
    weightage: float = 1.0
    target_value: float | None = None


@router.post("/cycles", summary="Create Review Cycle")
async def create_cycle(
    req: CreateCycleRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[PerformanceService, Depends(get_performance_service)],
) -> JSONResponse:
    cycle = await service.create_cycle(
        organization_id=ctx.organization_id,
        name=req.name,
        start_date=req.start_date,
        end_date=req.end_date,
        description=req.description,
    )
    return success_response(data=cycle.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/cycles", summary="List Review Cycles")
async def list_cycles(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[PerformanceService, Depends(get_performance_service)],
) -> JSONResponse:
    cycles = await service.list_cycles(ctx.organization_id)
    return success_response(data=[c.model_dump() for c in cycles])


@router.post("/goals", summary="Create Employee Goal")
async def create_goal(
    req: CreateGoalRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[PerformanceService, Depends(get_performance_service)],
) -> JSONResponse:
    goal = await service.create_goal(
        organization_id=ctx.organization_id,
        employee_id=req.employee_id,
        title=req.title,
        category=req.category,
        weightage=req.weightage,
        target_value=req.target_value,
    )
    return success_response(data=goal.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/goals/employee/{employee_id}", summary="List Employee Goals")
async def list_goals(
    employee_id: str,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[PerformanceService, Depends(get_performance_service)],
) -> JSONResponse:
    goals = await service.list_goals(ctx.organization_id, employee_id)
    return success_response(data=[g.model_dump() for g in goals])
