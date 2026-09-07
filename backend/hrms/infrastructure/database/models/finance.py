"""
SQLAlchemy Models - Invoice, InvoiceItem, Payment, Expense.
"""

from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class InvoiceModel(Base, TimestampMixin):
    """Client invoices."""
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("organization_id", "invoice_number", name="uq_invoice_number"),
        Index("ix_invoices_client", "organization_id", "client_id"),
        Index("ix_invoices_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    contract_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True)
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="SENT", nullable=False)  # DRAFT, SENT, PAID, PARTIALLY_PAID, OVERDUE, CANCELLED, VOID
    payment_terms: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class InvoiceItemModel(Base):
    """Line items on client invoices."""
    __tablename__ = "invoice_items"
    __table_args__ = (
        Index("ix_invoice_items_invoice", "organization_id", "invoice_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    invoice_id: Mapped[str] = mapped_column(String(64), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Float, default=18.0, nullable=False)


class PaymentModel(Base, TimestampMixin):
    """Payments received against invoices."""
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_invoice", "organization_id", "invoice_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    invoice_id: Mapped[str] = mapped_column(String(64), ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(32), default="BANK_TRANSFER", nullable=False)  # BANK_TRANSFER, CHEQUE, CASH, ONLINE, UPI
    reference_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="RECEIVED", nullable=False)  # RECEIVED, PENDING, FAILED, REFUNDED
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    received_by_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)


class ExpenseModel(Base, TimestampMixin):
    """Project and company operational expenses."""
    __tablename__ = "expenses"
    __table_args__ = (
        Index("ix_expenses_project", "organization_id", "project_id"),
        Index("ix_expenses_emp", "organization_id", "employee_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)  # TRAVEL, SOFTWARE, HARDWARE, OFFICE, TRAINING, CLIENT_ENTERTAINMENT, OTHER
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    receipt_storage_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="SUBMITTED", nullable=False)  # SUBMITTED, APPROVED, REJECTED, REIMBURSED
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reimbursed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
