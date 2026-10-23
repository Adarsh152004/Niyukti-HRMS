"""
API v1 — Deterministic HR Reporting Endpoints (`/api/v1/reports`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_reporting_service, get_tenant_context
from backend.api.response import success_response
from backend.hrms.application.report_service import ReportingService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.reports import ReportCategory

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


class CreateReportDefinitionRequest(BaseModel):
    title: str
    category: ReportCategory
    query_template: str
    output_columns: list[str]
    description: str = ""


@router.post("/definitions", summary="Create Report Definition")
async def create_definition(
    req: CreateReportDefinitionRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
) -> JSONResponse:
    definition = await service.create_definition(
        organization_id=ctx.organization_id,
        title=req.title,
        category=req.category,
        query_template=req.query_template,
        output_columns=req.output_columns,
        description=req.description,
    )
    return success_response(data=definition.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/definitions", summary="List Report Definitions")
async def list_definitions(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
) -> JSONResponse:
    definitions = await service.list_definitions(ctx.organization_id)
    return success_response(data=[d.model_dump() for d in definitions])


@router.post("/headcount/execute", summary="Execute Headcount Report")
async def execute_headcount_report(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[ReportingService, Depends(get_reporting_service)],
) -> JSONResponse:
    execution = await service.execute_headcount_report(ctx.organization_id, requested_by=ctx.actor_id)
    return success_response(data=execution.model_dump())
