"""
SQLAlchemy Model — Skill and EmployeeSkill (`skills` & `employee_skills` tables).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, TimestampMixin


class SkillModel(Base, TimestampMixin):
    """
    SQLAlchemy persistence model for Skill catalog entries.
    """

    __tablename__ = "skills"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_skill_org_name"),
        Index("ix_skills_org_id", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="TECHNICAL", nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class EmployeeSkillModel(Base, TimestampMixin):
    """
    SQLAlchemy persistence model for EmployeeSkill associations.
    """

    __tablename__ = "employee_skills"
    __table_args__ = (
        UniqueConstraint("organization_id", "employee_id", "skill_id", name="uq_emp_skill"),
        Index("ix_employee_skills_org_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(64), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency: Mapped[str] = mapped_column(String(32), default="INTERMEDIATE", nullable=False)
    years_experience: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
