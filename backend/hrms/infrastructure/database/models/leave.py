"""
SQLAlchemy Models - LeaveType, LeaveRequest.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, JSON, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class LeaveTypeModel(Base, TimestampMixin):
    """Leave policies and categories (Casual, Sick, Paid, Maternity, Earned)."""
    __tablename__ = "leave_types"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_leave_type_code"),
        Index("ix_leave_types_org", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    annual_quota: Mapped[float] = mapped_column(Float, default=12.0, nullable=False)
    carry_forward_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    carry_forward_max: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    encashment_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    applicable_gender: Mapped[str] = mapped_column(String(32), default="ALL", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class LeaveRequestModel(Base, TimestampMixin):
    """Employee leave applications."""
    __tablename__ = "leave_requests"
    __table_args__ = (
        Index("ix_leave_requests_emp", "organization_id", "employee_id"),
        Index("ix_leave_requests_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    leave_type_id: Mapped[str] = mapped_column(String(64), ForeignKey("leave_types.id", ondelete="RESTRICT"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_count: Mapped[float] = mapped_column(Float, nullable=False)
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED, CANCELLED
    applied_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approved_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    documents_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
