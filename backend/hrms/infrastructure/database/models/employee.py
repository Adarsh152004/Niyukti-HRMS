"""
SQLAlchemy Model — Employee (`employees` table).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import JSON, Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class EmployeeModel(Base, TimestampMixin):
    """
    SQLAlchemy persistence model for Employee entity.
    Self-referential manager_id relationship is carefully mapped.
    """

    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("organization_id", "employee_code", name="uq_employee_org_code"),
        UniqueConstraint("organization_id", "email", name="uq_employee_org_email"),
        Index("ix_employees_org_id", "organization_id"),
        Index("ix_employees_code", "organization_id", "employee_code"),
        Index("ix_employees_email", "organization_id", "email"),
        Index("ix_employees_dept_id", "department_id"),
        Index("ix_employees_des_id", "designation_id"),
        Index("ix_employees_manager_id", "manager_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_code: Mapped[str] = mapped_column(String(64), nullable=False)

    # Personal Details
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    preferred_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Organizational Placement
    department_id: Mapped[str] = mapped_column(String(64), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    designation_id: Mapped[str] = mapped_column(String(64), ForeignKey("designations.id", ondelete="RESTRICT"), nullable=False)
    manager_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)

    # Employment Information
    employment_status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    employment_type: Mapped[str] = mapped_column(String(32), default="FULL_TIME", nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Location & Timezone
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata", nullable=False)

    # Metadata
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Self-referential relationship for manager -> direct reports
    manager: Mapped[EmployeeModel | None] = relationship(
        "EmployeeModel",
        remote_side=[id],
        foreign_keys=[manager_id],
        backref="direct_reports",
    )
