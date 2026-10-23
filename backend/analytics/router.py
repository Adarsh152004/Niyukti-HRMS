"""
AI-Powered Intelligent HRMS — Analytics & KPI API Router.
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends

from backend.analytics.service import KPIService
from backend.api.middleware.auth import AuthPrincipal, get_current_principal

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & KPIs"])
kpi_service = KPIService()


@router.get("/dashboard", summary="Get executive workforce metrics")
async def get_dashboard(principal: AuthPrincipal = Depends(get_current_principal)) -> dict[str, Any]:
    metrics = kpi_service.get_executive_summary(tenant_id=principal.tenant_id)
    departments = kpi_service.get_department_breakdown(tenant_id=principal.tenant_id)
    ai_ops = kpi_service.get_ai_operations_metrics(tenant_id=principal.tenant_id)

    return {
        "summary": metrics.__dict__,
        "departments": departments,
        "ai_operations": ai_ops,
    }


@router.get("/departments", summary="Get department-level KPI breakdown")
async def get_departments(principal: AuthPrincipal = Depends(get_current_principal)) -> list[dict[str, Any]]:
    return kpi_service.get_department_breakdown(tenant_id=principal.tenant_id)


@router.get("/ai-ops", summary="Get AI fleet telemetry metrics")
async def get_ai_ops(principal: AuthPrincipal = Depends(get_current_principal)) -> dict[str, Any]:
    return kpi_service.get_ai_operations_metrics(tenant_id=principal.tenant_id)
