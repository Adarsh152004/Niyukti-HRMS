"""
HRMS Domain — PayrollRecord, SalaryComponent, Bonus, Deduction.

SENSITIVE PII: All salary fields are classified as SENSITIVE.
Payroll actions are HIGH-risk and require human approval before processing.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, generate_id, utc_now


class PayrollStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    PAID = "PAID"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class SalaryComponentType(StrEnum):
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"
    EMPLOYER_CONTRIBUTION = "EMPLOYER_CONTRIBUTION"


class SalaryComponent(HRMSBaseModel):
    """A named component of a salary structure (e.g., Basic Pay, HRA, PF)."""

    component_id: str = Field(default_factory=generate_id)
    organization_id: str
    name: str
    code: str
    component_type: SalaryComponentType
    description: str | None = Field(default=None)
    is_taxable: bool = Field(default=True)
    is_fixed: bool = Field(default=True, description="Fixed amount vs percentage of another component")
    percentage_of: str | None = Field(
        default=None,
        description="Component code this is a % of (if not fixed)",
    )
    percentage_value: float | None = Field(default=None, ge=0.0, le=100.0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)


class Bonus(HRMSBaseModel):
    """
    A one-time or periodic bonus payment.
    [PII:SENSITIVE] amount field.
    """

    bonus_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    bonus_type: str = Field(description="e.g. 'performance', 'festive', 'referral'")
    amount: float = Field(ge=0.0, description="[PII:SENSITIVE] Bonus amount")
    currency: str = Field(default="INR")
    reason: str | None = Field(default=None)
    approved_by: str | None = Field(default=None)
    approval_request_id: str | None = Field(default=None)
    payroll_period: str | None = Field(default=None, description="e.g. '2024-01'")
    is_paid: bool = Field(default=False)
    paid_on: date | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)


class Deduction(HRMSBaseModel):
    """
    A deduction from an employee's salary.
    [PII:SENSITIVE] amount field.
    """

    deduction_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    deduction_type: str = Field(description="e.g. 'advance', 'loan_repayment', 'penalty'")
    component_id: str | None = Field(default=None)
    amount: float = Field(ge=0.0, description="[PII:SENSITIVE] Deduction amount")
    currency: str = Field(default="INR")
    reason: str | None = Field(default=None)
    is_recurring: bool = Field(default=False)
    payroll_period: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)


class PayrollRecord(HRMSBaseModel):
    """
    A payroll processing record for one employee in one period.

    ALL amount fields are [PII:SENSITIVE].
    Payroll must be approved before processing (HIGH-risk action).
    """

    payroll_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    payroll_period: str = Field(description="ISO month format e.g. '2024-01'")
    period_start: date
    period_end: date

    # Earnings — [PII:SENSITIVE]
    gross_salary: float = Field(ge=0.0, description="[PII:SENSITIVE]")
    basic_salary: float = Field(ge=0.0, description="[PII:SENSITIVE]")
    allowances: float = Field(default=0.0, ge=0.0, description="[PII:SENSITIVE]")
    overtime_pay: float = Field(default=0.0, ge=0.0, description="[PII:SENSITIVE]")
    bonus_amount: float = Field(default=0.0, ge=0.0, description="[PII:SENSITIVE]")

    # Deductions — [PII:SENSITIVE]
    total_deductions: float = Field(default=0.0, ge=0.0, description="[PII:SENSITIVE]")
    income_tax: float = Field(default=0.0, ge=0.0, description="[PII:SENSITIVE]")
    pf_employee: float = Field(default=0.0, ge=0.0, description="[PII:SENSITIVE] PF contribution")
    other_deductions: float = Field(default=0.0, ge=0.0, description="[PII:SENSITIVE]")

    # Net — [PII:SENSITIVE]
    net_salary: float = Field(ge=0.0, description="[PII:SENSITIVE]")

    # Days & hours
    working_days: float = Field(default=0.0, ge=0.0)
    days_present: float = Field(default=0.0, ge=0.0)
    days_absent: float = Field(default=0.0, ge=0.0)
    leave_days_used: float = Field(default=0.0, ge=0.0)

    # Status and approval
    status: PayrollStatus = Field(default=PayrollStatus.DRAFT)
    approval_request_id: str | None = Field(
        default=None,
        description="Approval request ID — payroll cannot be processed without approval",
    )
    approved_by: str | None = Field(default=None)
    approved_at: datetime | None = Field(default=None)
    processed_by: str | None = Field(default=None)
    processed_at: datetime | None = Field(default=None)
    payment_date: date | None = Field(default=None)
    payment_reference: str | None = Field(default=None)

    # Component breakdown
    component_breakdown: list[dict[str, float]] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
