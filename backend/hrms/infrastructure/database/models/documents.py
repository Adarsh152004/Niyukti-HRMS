"""
SQLAlchemy Model — EmployeeDocument (`employee_documents` table).
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class EmployeeDocumentModel(Base):
    """
    SQLAlchemy persistence model for EmployeeDocument metadata.
    Does NOT store raw document binary content — storage_reference is an opaque key.
    """

    __tablename__ = "employee_documents"
    __table_args__ = (
        Index("ix_documents_org_emp", "organization_id", "employee_id"),
        Index("ix_documents_org_id", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(64), default="OTHER", nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), default="application/pdf", nullable=False)
    size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="UNVERIFIED", nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
