"""
SQLAlchemy Model - Polymorphic Document Vault.
"""

from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class DocumentModel(Base, TimestampMixin):
    """Universal document metadata model supporting any parent entity."""
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_entity", "organization_id", "entity_type", "entity_id"),
        Index("ix_documents_category", "organization_id", "category"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)  # PDF, DOCX, PNG, ZIP
    mime_type: Mapped[str] = mapped_column(String(128), default="application/pdf", nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # EMPLOYEE, CANDIDATE, CLIENT, PROJECT, CONTRACT, TASK, TICKET, INVOICE
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="GENERAL", nullable=False)  # GENERAL, CONTRACT, PROPOSAL, INVOICE, RESUME, ID_PROOF, CERTIFICATE, SCREENSHOT, DELIVERABLE
    uploaded_by_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
