"""
Tests for 100% Deterministic Payroll Engine and Salary Component Breakdown.
"""

from __future__ import annotations

import pytest

from backend.hrms.application.payroll_service import PayrollService
from backend.hrms.domain.payroll import SalaryComponentType
from backend.hrms.infrastructure.memory_repositories import InMemoryPayrollRepository


@pytest.mark.asyncio
async def test_payroll_deterministic_calculation_and_components():
    repo = InMemoryPayrollRepository()
    svc = PayrollService(repo)
    org_id = "org-payroll-test"

    # 1. Add salary components
    comp1 = await svc.add_salary_component(org_id, "Basic Pay", "BASIC", SalaryComponentType.EARNING)
    comp2 = await svc.add_salary_component(
        org_id, "House Rent Allowance", "HRA", SalaryComponentType.EARNING, percentage_of="BASIC", percentage_value=40.0
    )
    assert comp1.name == "Basic Pay"
    assert comp2.percentage_value == 40.0

    # 2. Pure deterministic calculation
    res = svc.calculate_payslip_deterministic(
        base_salary=10000.0,
        housing_allowance=2000.0,
        transport_allowance=500.0,
        bonus=1500.0,
        tax_rate=0.20,
        pf_rate=0.05,
    )

    # Gross = 10000 + 2000 + 500 + 1500 = 14000
    assert res["gross_pay"] == 14000.0
    # Tax = 14000 * 0.20 = 2800
    assert res["income_tax"] == 2800.0
    # PF = 10000 * 0.05 = 500
    assert res["provident_fund"] == 500.0
    # Total Deductions = 3300
    assert res["total_deductions"] == 3300.0
    # Net Pay = 14000 - 3300 = 10700
    assert res["net_pay"] == 10700.0
    assert res["is_deterministic"] is True
