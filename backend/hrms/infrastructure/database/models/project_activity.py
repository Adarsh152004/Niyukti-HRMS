"""
SQLAlchemy Models - ChangeRequest, Release.
"""

from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class ChangeRequestModel(Base, TimestampMixin):
    """Client requested project scope changes."""
    __tablename__ = "change_requests"
    __table_args__ = (
        Index("ix_change_requests_proj", "organization_id", "project_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    client_contact_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("client_contacts.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2048), nullable=False)
    impact_analysis: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    estimated_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cost_impact: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="SUBMITTED", nullable=False)  # SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, IMPLEMENTED
    priority: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_by_employee_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class ReleaseModel(Base, TimestampMixin):
    """Software deployments and releases."""
    __tablename__ = "releases"
    __table_args__ = (
        Index("ix_releases_proj", "organization_id", "project_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)  # v1.0.0
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    release_notes: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    environment: Mapped[str] = mapped_column(String(32), default="PRODUCTION", nullable=False)  # STAGING, PRODUCTION
    status: Mapped[str] = mapped_column(String(32), default="RELEASED", nullable=False)  # PLANNED, IN_PROGRESS, RELEASED, ROLLED_BACK
    released_by_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
