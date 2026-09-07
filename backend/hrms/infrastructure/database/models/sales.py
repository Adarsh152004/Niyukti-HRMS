"""
SQLAlchemy Models - ClientRequirement, Proposal, Quotation, QuotationItem, Contract.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, JSON, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class ClientRequirementModel(Base, TimestampMixin):
    """Client project request requirements."""
    __tablename__ = "client_requirements"
    __table_args__ = (
        Index("ix_client_reqs_client", "organization_id", "client_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2048), nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(64), default="NEW_PROJECT", nullable=False)  # NEW_PROJECT, ENHANCEMENT, SUPPORT, CONSULTATION
    priority: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="SUBMITTED", nullable=False)  # DRAFT, SUBMITTED, UNDER_ANALYSIS, ACCEPTED, DECLINED
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    analyzed_by_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)


class ProposalModel(Base, TimestampMixin):
    """Technical proposals for client requirements."""
    __tablename__ = "proposals"
    __table_args__ = (
        Index("ix_proposals_client", "organization_id", "client_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    requirement_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("client_requirements.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    scope_of_work: Mapped[str] = mapped_column(String(2048), nullable=False)
    technical_approach: Mapped[str] = mapped_column(String(2048), nullable=False)
    estimated_duration_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    estimated_team_size: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)  # DRAFT, SENT, UNDER_REVIEW, ACCEPTED, REJECTED, REVISED
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    prepared_by_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)


class QuotationModel(Base, TimestampMixin):
    """Formal financial quotations."""
    __tablename__ = "quotations"
    __table_args__ = (
        UniqueConstraint("organization_id", "quotation_number", name="uq_quotation_number"),
        Index("ix_quotations_client", "organization_id", "client_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    proposal_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("proposals.id", ondelete="SET NULL"), nullable=True)
    quotation_number: Mapped[str] = mapped_column(String(64), nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tax_percentage: Mapped[float] = mapped_column(Float, default=18.0, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)  # DRAFT, SENT, ACCEPTED, REJECTED, EXPIRED
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)


class QuotationItemModel(Base):
    """Line items for financial quotations."""
    __tablename__ = "quotation_items"
    __table_args__ = (
        Index("ix_quotation_items_quotation", "organization_id", "quotation_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    quotation_id: Mapped[str] = mapped_column(String(64), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), default="HOURS", nullable=False)  # HOURS, DAYS, FIXED, MONTHLY


class ContractModel(Base, TimestampMixin):
    """Signed legal client contracts."""
    __tablename__ = "contracts"
    __table_args__ = (
        UniqueConstraint("organization_id", "contract_number", name="uq_contract_number"),
        Index("ix_contracts_client", "organization_id", "client_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    quotation_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("quotations.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    contract_number: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(64), default="FIXED_PRICE", nullable=False)  # FIXED_PRICE, TIME_MATERIAL, RETAINER, SUPPORT
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_value: Mapped[float] = mapped_column(Float, nullable=False)
    payment_terms: Mapped[str | None] = mapped_column(String(512), nullable=True)
    auto_renewal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)  # DRAFT, ACTIVE, COMPLETED, TERMINATED, EXPIRED
    signed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_storage_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
