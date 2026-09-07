"""
SQLAlchemy Models - SupportContract, SupportTicket, TicketComment, TicketAssignment.
"""

from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class SupportContractModel(Base, TimestampMixin):
    """Post-delivery maintenance & support SLA contracts."""
    __tablename__ = "support_contracts"
    __table_args__ = (
        UniqueConstraint("organization_id", "contract_number", name="uq_support_contract_num"),
        Index("ix_support_contracts_client", "organization_id", "client_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    contract_number: Mapped[str] = mapped_column(String(64), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(32), default="STANDARD", nullable=False)  # BASIC, STANDARD, PREMIUM, ENTERPRISE
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    monthly_hours_included: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)
    hourly_rate_excess: Mapped[float] = mapped_column(Float, default=1500.0, nullable=False)
    response_time_hours: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    resolution_time_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)  # ACTIVE, EXPIRED, CANCELLED
    auto_renewal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SupportTicketModel(Base, TimestampMixin):
    """Client issues, bugs, and maintenance support tickets."""
    __tablename__ = "support_tickets"
    __table_args__ = (
        UniqueConstraint("organization_id", "ticket_number", name="uq_support_ticket_num"),
        Index("ix_support_tickets_client", "organization_id", "client_id"),
        Index("ix_support_tickets_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    support_contract_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("support_contracts.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    ticket_number: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2048), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="BUG", nullable=False)  # BUG, FEATURE_REQUEST, QUESTION, INCIDENT, MAINTENANCE
    priority: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status: Mapped[str] = mapped_column(String(32), default="OPEN", nullable=False)  # OPEN, IN_PROGRESS, WAITING_ON_CLIENT, RESOLVED, CLOSED, REOPENED
    reported_by_client_contact_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("client_contacts.id", ondelete="SET NULL"), nullable=True)
    assigned_to_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    estimated_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TicketCommentModel(Base, TimestampMixin):
    """Discussion and updates on support tickets."""
    __tablename__ = "ticket_comments"
    __table_args__ = (
        Index("ix_ticket_comments_ticket", "organization_id", "ticket_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    author_type: Mapped[str] = mapped_column(String(32), default="EMPLOYEE", nullable=False)  # EMPLOYEE, CLIENT
    author_id: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TicketAssignmentModel(Base):
    """Assignment and escalation history for support tickets."""
    __tablename__ = "ticket_assignments"
    __table_args__ = (
        Index("ix_ticket_assignments_ticket", "organization_id", "ticket_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    ticket_id: Mapped[str] = mapped_column(String(64), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    assigned_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
