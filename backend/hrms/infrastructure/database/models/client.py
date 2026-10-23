"""
SQLAlchemy Models - Client, ClientContact, ClientAddress, Lead, ClientCommunication, ClientNote.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class ClientModel(Base, TimestampMixin):
    """Client organizations that commission digital platform software."""
    __tablename__ = "clients"
    __table_args__ = (
        UniqueConstraint("organization_id", "company_name", name="uq_client_org_company"),
        Index("ix_clients_org", "organization_id"),
        Index("ix_clients_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)  # PROSPECT, ACTIVE, INACTIVE, CHURNED
    source: Mapped[str] = mapped_column(String(64), default="REFERRAL", nullable=False)
    converted_from_lead_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    account_manager_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1024), nullable=True)


class ClientContactModel(Base, TimestampMixin):
    """Primary and secondary contacts at client organizations."""
    __tablename__ = "client_contacts"
    __table_args__ = (
        Index("ix_client_contacts_client", "organization_id", "client_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(128), nullable=True)
    department: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_billing_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class ClientAddressModel(Base, TimestampMixin):
    """Billing and branch addresses for client companies."""
    __tablename__ = "client_addresses"
    __table_args__ = (
        Index("ix_client_addresses_client", "organization_id", "client_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(64), default="HQ", nullable=False)  # HQ, BILLING, BRANCH
    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(128), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(32), nullable=False)
    country: Mapped[str] = mapped_column(String(64), default="India", nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class LeadModel(Base, TimestampMixin):
    """Prospective business leads before converting to client."""
    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_org_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="WEBSITE", nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    estimated_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="NEW", nullable=False)  # NEW, CONTACTED, QUALIFIED, PROPOSAL_SENT, NEGOTIATION, WON, LOST
    assigned_to_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    converted_to_client_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    lost_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class ClientCommunicationModel(Base, TimestampMixin):
    """Interaction history with clients and leads."""
    __tablename__ = "client_communications"
    __table_args__ = (
        Index("ix_client_comms_client", "organization_id", "client_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("clients.id", ondelete="CASCADE"), nullable=True)
    lead_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("leads.id", ondelete="CASCADE"), nullable=True)
    comm_type: Mapped[str] = mapped_column(String(32), default="EMAIL", nullable=False)  # EMAIL, CALL, MEETING, NOTE
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(String(2048), nullable=False)
    direction: Mapped[str] = mapped_column(String(32), default="OUTBOUND", nullable=False)  # INBOUND, OUTBOUND
    employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
