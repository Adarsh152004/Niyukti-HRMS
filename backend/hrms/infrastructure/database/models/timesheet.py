"""
SQLAlchemy Models - Timesheet, TimesheetEntry.
"""

from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class TimesheetModel(Base, TimestampMixin):
    """Weekly/Monthly employee timesheets."""
    __tablename__ = "timesheets"
    __table_args__ = (
        UniqueConstraint("organization_id", "employee_id", "period_start", name="uq_timesheet_emp_period"),
        Index("ix_timesheets_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    total_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)  # DRAFT, SUBMITTED, APPROVED, REJECTED
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TimesheetEntryModel(Base):
    """Individual task time allocation entry."""
    __tablename__ = "timesheet_entries"
    __table_args__ = (
        Index("ix_timesheet_entries_ts", "organization_id", "timesheet_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    timesheet_id: Mapped[str] = mapped_column(String(64), ForeignKey("timesheets.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
