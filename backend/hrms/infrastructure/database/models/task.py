"""
SQLAlchemy Models - Task, TaskAssignment.
"""

from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class TaskModel(Base, TimestampMixin):
    """Development tasks, user stories, and bugs."""
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_project", "organization_id", "project_id"),
        Index("ix_tasks_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_task_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    milestone_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("milestones.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    task_type: Mapped[str] = mapped_column(String(32), default="FEATURE", nullable=False)  # FEATURE, BUG, IMPROVEMENT, TASK, STORY, EPIC
    status: Mapped[str] = mapped_column(String(32), default="TODO", nullable=False)  # BACKLOG, TODO, IN_PROGRESS, IN_REVIEW, TESTING, DONE, CLOSED
    priority: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    estimated_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)


class TaskAssignmentModel(Base):
    """Task assignee mapping."""
    __tablename__ = "task_assignments"
    __table_args__ = (
        UniqueConstraint("organization_id", "task_id", "employee_id", name="uq_task_assignment"),
        Index("ix_task_assignments_task", "organization_id", "task_id"),
        Index("ix_task_assignments_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[str] = mapped_column(String(64), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    assigned_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
