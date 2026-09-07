"""
API v1 — Payroll Endpoints (`/api/v1/payroll`).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_payroll_service, get_tenant_context
from backend.api.response import success_response
from backend.hrms.application.payroll_service import PayrollService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.payroll import SalaryComponentType

router = APIRouter(prefix="/api/v1/payroll", tags=["Payroll"])


class CreateComponentRequest(BaseModel):
    name: str
    code: str
    component_type: SalaryComponentType
    percentage_of: str | None = None
    percentage_value: float | None = None


class CalculatePayslipRequest(BaseModel):
    base_salary: float
    housing_allowance: float = 0.0
    transport_allowance: float = 0.0
    bonus: float = 0.0
    tax_rate: float = 0.20
    pf_rate: float = 0.05


@router.post("/components", summary="Create Salary Component")
async def create_component(
    req: CreateComponentRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[PayrollService, Depends(get_payroll_service)],
) -> JSONResponse:
    comp = await service.add_salary_component(
        organization_id=ctx.organization_id,
        name=req.name,
        code=req.code,
        component_type=req.component_type,
        percentage_of=req.percentage_of,
        percentage_value=req.percentage_value,
    )
    return success_response(data=comp.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/components", summary="List Salary Components")
async def list_components(
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[PayrollService, Depends(get_payroll_service)],
) -> JSONResponse:
    components = await service.list_components(ctx.organization_id)
    return success_response(data=[c.model_dump() for c in components])


@router.post("/calculate-payslip", summary="Calculate Payslip Deterministically")
async def calculate_payslip(
    req: CalculatePayslipRequest,
    ctx: Annotated[TenantContext, Depends(get_tenant_context)],
    service: Annotated[PayrollService, Depends(get_payroll_service)],
) -> JSONResponse:
    res = service.calculate_payslip_deterministic(
        base_salary=req.base_salary,
        housing_allowance=req.housing_allowance,
        transport_allowance=req.transport_allowance,
        bonus=req.bonus,
        tax_rate=req.tax_rate,
        pf_rate=req.pf_rate,
    )
    return success_response(data=res)
