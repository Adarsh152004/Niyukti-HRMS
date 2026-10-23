"""HRMS Domain — AttendanceRecord, Shift, Holiday."""

from __future__ import annotations

from datetime import date, datetime, time

from pydantic import Field

from backend.hrms.domain.common import AttendanceStatus, HRMSBaseModel, generate_id, utc_now


class Shift(HRMSBaseModel):
    """Work shift definition."""

    shift_id: str = Field(default_factory=generate_id)
    organization_id: str
    name: str = Field(description="e.g. 'Morning Shift', 'Night Shift'")
    code: str | None = Field(default=None)
    start_time: time
    end_time: time
    duration_hours: float = Field(ge=0.0)
    break_duration_minutes: int = Field(default=30, ge=0)
    is_overnight: bool = Field(default=False)
    is_flexible: bool = Field(default=False)
    grace_period_minutes: int = Field(default=10, description="Minutes late before marked as LATE")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)


class AttendanceRecord(HRMSBaseModel):
    """Daily attendance record for an employee."""

    attendance_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    date: date
    shift_id: str | None = Field(default=None)
    status: AttendanceStatus = Field(default=AttendanceStatus.PRESENT)
    check_in_time: datetime | None = Field(default=None)
    check_out_time: datetime | None = Field(default=None)
    work_hours: float | None = Field(default=None, ge=0.0)
    overtime_hours: float = Field(default=0.0, ge=0.0)
    late_minutes: int = Field(default=0, ge=0)
    early_departure_minutes: int = Field(default=0, ge=0)
    biometric_record_id: str | None = Field(default=None, description="Reference to biometric device record")
    is_regularized: bool = Field(
        default=False,
        description="True if HR manually corrected this record",
    )
    regularized_by: str | None = Field(default=None)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Holiday(HRMSBaseModel):
    """A public or organizational holiday."""

    holiday_id: str = Field(default_factory=generate_id)
    organization_id: str
    name: str
    date: date
    holiday_type: str = Field(
        default="PUBLIC",
        description="e.g. 'PUBLIC', 'RESTRICTED', 'OPTIONAL', 'COMPANY'",
    )
    description: str | None = Field(default=None)
    applicable_departments: list[str] = Field(
        default_factory=list,
        description="Empty = applies to all departments",
    )
    applicable_locations: list[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)
