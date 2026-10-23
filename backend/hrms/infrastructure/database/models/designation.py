"""
SQLAlchemy Model — Designation (`designations` table).
"""

from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, TimestampMixin


class DesignationModel(Base, TimestampMixin):
    """
    SQLAlchemy persistence model for Designation.
    """

    __tablename__ = "designations"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_designation_org_code"),
        Index("ix_designations_org_id", "organization_id"),
        Index("ix_designations_dept_id", "department_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    department_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    min_experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_managerial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
