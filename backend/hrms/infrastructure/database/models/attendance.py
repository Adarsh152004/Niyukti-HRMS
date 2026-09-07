"""
SQLAlchemy Models - WorkSchedule, Shift, EmployeeWorkSchedule, AttendanceRecord, Holiday.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, JSON, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class WorkScheduleModel(Base, TimestampMixin):
    """Work schedule policy definitions."""
    __tablename__ = "work_schedules"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_work_schedule_code"),
        Index("ix_work_schedules_org", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(32), default="FIXED", nullable=False)  # FIXED, FLEXIBLE, SHIFT
    working_days_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)  # ["MON", "TUE", "WED", "THU", "FRI"]
    default_start_time: Mapped[str] = mapped_column(String(16), default="09:00", nullable=False)
    default_end_time: Mapped[str] = mapped_column(String(16), default="18:00", nullable=False)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class ShiftModel(Base, TimestampMixin):
    """Work shift windows (Morning, Evening, Night)."""
    __tablename__ = "shifts"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_shift_code"),
        Index("ix_shifts_org", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    start_time: Mapped[str] = mapped_column(String(16), nullable=False)
    end_time: Mapped[str] = mapped_column(String(16), nullable=False)
    break_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    grace_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    is_night_shift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class EmployeeWorkScheduleModel(Base, TimestampMixin):
    """Assignment of work schedules and shifts to employees."""
    __tablename__ = "employee_work_schedules"
    __table_args__ = (
        Index("ix_emp_work_schedules_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    work_schedule_id: Mapped[str] = mapped_column(String(64), ForeignKey("work_schedules.id", ondelete="RESTRICT"), nullable=False)
    shift_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("shifts.id", ondelete="SET NULL"), nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class AttendanceRecordModel(Base, TimestampMixin):
    """Daily check-in and check-out attendance records."""
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("organization_id", "employee_id", "date", name="uq_attendance_emp_date"),
        Index("ix_attendance_emp_date", "organization_id", "employee_id", "date"),
        Index("ix_attendance_date", "organization_id", "date"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    break_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    break_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PRESENT", nullable=False)  # PRESENT, ABSENT, HALF_DAY, REMOTE, ON_LEAVE, LATE
    source: Mapped[str] = mapped_column(String(32), default="MANUAL", nullable=False)  # BIOMETRIC, MANUAL, SYSTEM, MOBILE_APP
    overtime_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    remarks: Mapped[str | None] = mapped_column(String(512), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)


class HolidayModel(Base, TimestampMixin):
    """Holiday calendar entries."""
    __tablename__ = "holidays"
    __table_args__ = (
        UniqueConstraint("organization_id", "date", "name", name="uq_holiday_org_date_name"),
        Index("ix_holidays_org_date", "organization_id", "date"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    holiday_type: Mapped[str] = mapped_column(String(32), default="PUBLIC", nullable=False)  # PUBLIC, COMPANY, OPTIONAL
    applicable_departments_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
