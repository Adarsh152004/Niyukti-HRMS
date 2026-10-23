"""
SQLAlchemy Model — Organization / Tenant (`organizations` table).
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, TimestampMixin


class OrganizationModel(Base, TimestampMixin):
    """
    SQLAlchemy persistence model for Organization (Tenant).
    """

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country: Mapped[str] = mapped_column(String(8), default="IN", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata", nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", index=True, nullable=False)

    registration_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    employee_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
