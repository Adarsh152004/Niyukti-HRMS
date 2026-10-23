"""
AI-Powered Intelligent HRMS — Deterministic Payroll Synthetic Data Generator.

Generates:
- Monthly payroll batch runs
- Deterministic statutory calculations (EPF 12%, TDS income tax withholding, Health fund)
- Detailed individual employee payslips
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from backend.database.seeder.generators.employee_generator import SyntheticEmployee


@dataclass
class SyntheticPayslip:
    id: str
    payroll_run_id: str
    employee_id: str
    employee_name: str
    organization_id: str
    period: str
    gross_earnings: float
    base_salary: float
    special_allowance: float
    epf_deduction: float
    tds_tax_deduction: float
    other_deductions: float
    total_deductions: float
    net_payable: float
    currency: str = "USD"
    status: str = "PROCESSED"


@dataclass
class SyntheticPayrollRun:
    id: str
    organization_id: str
    period: str
    total_employees: int
    total_gross: float
    total_deductions: float
    total_net_disbursed: float
    status: str  # DRAFT, CALCULATED, AUDITED, APPROVED, DISBURSED
    payslips: list[SyntheticPayslip]


def generate_payroll_runs(
    employees: list[SyntheticEmployee],
    months_count: int = 3,
    seed: int = 42,
) -> list[SyntheticPayrollRun]:
    """Generates deterministic monthly payroll runs with complete statutory breakdown."""
    rng = random.Random(seed)
    payroll_runs: list[SyntheticPayrollRun] = []

    if not employees:
        return []

    org_id = employees[0].organization_id
    periods = ["2026-08", "2026-07", "2026-06"][:months_count]

    for p_idx, period in enumerate(periods):
        run_id = f"payrun-{org_id}-{period}"
        payslips: list[SyntheticPayslip] = []

        total_gross = 0.0
        total_ded = 0.0
        total_net = 0.0

        for emp in employees:
            if emp.status != "active":
                continue

            monthly_annual = emp.salary / 12.0
            base = round(monthly_annual * 0.50, 2)
            special = round(monthly_annual * 0.50, 2)
            gross = base + special

            # Deterministic Statutory Deductions
            epf = round(base * 0.12, 2)
            # Tiered tax rate approximation
            tax_rate = 0.22 if emp.level >= 6 else 0.15 if emp.level >= 3 else 0.10
            tds = round(gross * tax_rate, 2)
            other = 200.0  # Professional tax / benefits fund

            deductions = epf + tds + other
            net = gross - deductions

            slip = SyntheticPayslip(
                id=f"slip-{run_id}-{emp.id}",
                payroll_run_id=run_id,
                employee_id=emp.id,
                employee_name=emp.full_name,
                organization_id=org_id,
                period=period,
                gross_earnings=gross,
                base_salary=base,
                special_allowance=special,
                epf_deduction=epf,
                tds_tax_deduction=tds,
                other_deductions=other,
                total_deductions=deductions,
                net_payable=round(net, 2),
            )
            payslips.append(slip)
            total_gross += gross
            total_ded += deductions
            total_net += net

        run_status = "APPROVED" if p_idx == 0 else "DISBURSED"

        payroll_runs.append(
            SyntheticPayrollRun(
                id=run_id,
                organization_id=org_id,
                period=period,
                total_employees=len(payslips),
                total_gross=round(total_gross, 2),
                total_deductions=round(total_ded, 2),
                total_net_disbursed=round(total_net, 2),
                status=run_status,
                payslips=payslips,
            )
        )

    return payroll_runs
