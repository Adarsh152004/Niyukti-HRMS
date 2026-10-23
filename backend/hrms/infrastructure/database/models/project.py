"""
SQLAlchemy Models - Project, ProjectMember, Milestone.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class ProjectModel(Base, TimestampMixin):
    """Digital platform / software software projects."""
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_project_code"),
        Index("ix_projects_client", "organization_id", "client_id"),
        Index("ix_projects_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(2048), nullable=False)
    project_type: Mapped[str] = mapped_column(String(64), default="FIXED_PRICE", nullable=False)  # FIXED_PRICE, TIME_AND_MATERIAL, RETAINER, INTERNAL
    status: Mapped[str] = mapped_column(String(32), default="PLANNING", nullable=False)  # PLANNING, IN_PROGRESS, ON_HOLD, COMPLETED, CANCELLED, MAINTENANCE
    priority: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    estimated_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    budget_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    technology_stack_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    repository_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    project_manager_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)


class ProjectMemberModel(Base):
    """Employee allocation to projects."""
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "project_id", "employee_id", name="uq_proj_member"),
        Index("ix_proj_members_proj", "organization_id", "project_id"),
        Index("ix_proj_members_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(64), default="DEVELOPER", nullable=False)  # PM, TECH_LEAD, DEVELOPER, DESIGNER, QA, BA, DEVOPS
    allocation_percentage: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class MilestoneModel(Base, TimestampMixin):
    """Project phases and milestones."""
    __tablename__ = "milestones"
    __table_args__ = (
        Index("ix_milestones_proj", "organization_id", "project_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)  # PENDING, IN_PROGRESS, COMPLETED, OVERDUE
    deliverables_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    payment_linked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payment_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
