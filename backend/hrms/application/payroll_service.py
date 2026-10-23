"""
Payroll Application Service — 100% Deterministic Gross-To-Net Calculation and Component Breakdown.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.payroll import SalaryComponent, SalaryComponentType
from backend.hrms.ports.repositories import PayrollRepository


class PayrollService(BaseApplicationService):
    """
    Deterministic payroll calculation engine.
    CORE INVARIANT: Payroll and taxation math are 100% deterministic and NEVER calculated by an LLM.
    """

    def __init__(self, payroll_repo: PayrollRepository) -> None:
        super().__init__()
        self.repo = payroll_repo

    async def add_salary_component(
        self,
        organization_id: str,
        name: str,
        code: str,
        component_type: SalaryComponentType,
        percentage_of: str | None = None,
        percentage_value: float | None = None,
    ) -> SalaryComponent:
        comp = SalaryComponent(
            organization_id=organization_id,
            name=name,
            code=code,
            component_type=component_type,
            is_fixed=percentage_of is None,
            percentage_of=percentage_of,
            percentage_value=percentage_value,
        )
        return await self.repo.create_component(comp)

    def calculate_payslip_deterministic(
        self,
        base_salary: float,
        housing_allowance: float = 0.0,
        transport_allowance: float = 0.0,
        tax_rate: float = 0.20,
        pf_rate: float = 0.05,
        bonus: float = 0.0,
    ) -> dict[str, Any]:
        """
        Pure deterministic formula:
        Gross = Base + Housing + Transport + Bonus
        Deductions = Tax (Gross * tax_rate) + Provident Fund (Base * pf_rate)
        Net = Gross - Deductions
        """
        gross_pay = round(base_salary + housing_allowance + transport_allowance + bonus, 2)
        income_tax = round(gross_pay * tax_rate, 2)
        provident_fund = round(base_salary * pf_rate, 2)
        total_deductions = round(income_tax + provident_fund, 2)
        net_pay = round(gross_pay - total_deductions, 2)

        return {
            "base_salary": base_salary,
            "housing_allowance": housing_allowance,
            "transport_allowance": transport_allowance,
            "bonus": bonus,
            "gross_pay": gross_pay,
            "income_tax": income_tax,
            "provident_fund": provident_fund,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
            "currency": "USD",
            "is_deterministic": True,
        }

    async def list_components(self, organization_id: str) -> Sequence[SalaryComponent]:
        return await self.repo.list_components(organization_id)
