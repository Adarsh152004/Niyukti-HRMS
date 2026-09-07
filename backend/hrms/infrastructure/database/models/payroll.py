"""
SQLAlchemy Models - Payroll Entities.
"""

from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class SalaryComponentModel(Base, TimestampMixin):
    """Salary component catalog (Basic, HRA, Medical, PF, Tax, Bonus)."""
    __tablename__ = "salary_components"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_salary_component_code"),
        Index("ix_salary_components_org", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    component_type: Mapped[str] = mapped_column(String(32), nullable=False)  # EARNING, DEDUCTION, EMPLOYER_CONTRIBUTION
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    calculation_type: Mapped[str] = mapped_column(String(32), default="FIXED", nullable=False)  # FIXED, PERCENTAGE
    percentage_of_component_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class SalaryStructureModel(Base, TimestampMixin):
    """Template salary structure."""
    __tablename__ = "salary_structures"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_salary_structure_code"),
        Index("ix_salary_structures_org", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    base_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class SalaryStructureComponentModel(Base):
    """Junction mapping salary components inside a structure."""
    __tablename__ = "salary_structure_components"
    __table_args__ = (
        UniqueConstraint("organization_id", "structure_id", "component_id", name="uq_struct_component"),
        Index("ix_struct_components_struct", "organization_id", "structure_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    structure_id: Mapped[str] = mapped_column(String(64), ForeignKey("salary_structures.id", ondelete="CASCADE"), nullable=False)
    component_id: Mapped[str] = mapped_column(String(64), ForeignKey("salary_components.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    formula: Mapped[str | None] = mapped_column(String(255), nullable=True)


class EmployeeSalaryRecordModel(Base, TimestampMixin):
    """Historical salary record for employees (preserves revision history)."""
    __tablename__ = "employee_salary_records"
    __table_args__ = (
        Index("ix_emp_salary_records_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    salary_structure_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("salary_structures.id", ondelete="SET NULL"), nullable=True)
    ctc_annual: Mapped[float] = mapped_column(Float, nullable=False)
    base_monthly: Mapped[float] = mapped_column(Float, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    revision_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revised_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="CURRENT", nullable=False)  # CURRENT, HISTORICAL


class EmployeeSalaryComponentModel(Base):
    """Breakdown components of an active employee salary record."""
    __tablename__ = "employee_salary_components"
    __table_args__ = (
        Index("ix_emp_salary_components_rec", "organization_id", "salary_record_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    salary_record_id: Mapped[str] = mapped_column(String(64), ForeignKey("employee_salary_records.id", ondelete="CASCADE"), nullable=False)
    component_id: Mapped[str] = mapped_column(String(64), ForeignKey("salary_components.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)


class PayrollPeriodModel(Base, TimestampMixin):
    """Payroll accounting period (e.g. October 2026)."""
    __tablename__ = "payroll_periods"
    __table_args__ = (
        UniqueConstraint("organization_id", "month", "year", name="uq_payroll_period_m_y"),
        Index("ix_payroll_periods_org", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="OPEN", nullable=False)  # OPEN, PROCESSING, CLOSED, LOCKED


class PayrollRunModel(Base, TimestampMixin):
    """Payroll execution summary run."""
    __tablename__ = "payroll_runs"
    __table_args__ = (
        Index("ix_payroll_runs_period", "organization_id", "period_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    period_id: Mapped[str] = mapped_column(String(64), ForeignKey("payroll_periods.id", ondelete="RESTRICT"), nullable=False)
    run_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_gross: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_deductions: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_net: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    employee_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)  # DRAFT, CALCULATED, APPROVED, PAID
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PayslipModel(Base, TimestampMixin):
    """Individual employee monthly payslip."""
    __tablename__ = "payslips"
    __table_args__ = (
        UniqueConstraint("organization_id", "run_id", "employee_id", name="uq_payslip_run_emp"),
        Index("ix_payslips_run", "organization_id", "run_id"),
        Index("ix_payslips_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    gross_pay: Mapped[float] = mapped_column(Float, nullable=False)
    total_deductions: Mapped[float] = mapped_column(Float, nullable=False)
    net_pay: Mapped[float] = mapped_column(Float, nullable=False)
    days_worked: Mapped[float] = mapped_column(Float, nullable=False)
    days_absent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overtime_pay: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="GENERATED", nullable=False)  # GENERATED, RELEASED, PAID


class PayslipItemModel(Base):
    """Itemized earnings and deductions on a payslip."""
    __tablename__ = "payslip_items"
    __table_args__ = (
        Index("ix_payslip_items_payslip", "organization_id", "payslip_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    payslip_id: Mapped[str] = mapped_column(String(64), ForeignKey("payslips.id", ondelete="CASCADE"), nullable=False)
    component_id: Mapped[str] = mapped_column(String(64), ForeignKey("salary_components.id", ondelete="RESTRICT"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(32), nullable=False)  # EARNING, DEDUCTION
    amount: Mapped[float] = mapped_column(Float, nullable=False)
