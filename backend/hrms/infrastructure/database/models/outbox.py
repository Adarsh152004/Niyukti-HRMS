"""
SQLAlchemy Model — Transactional Outbox Event (`outbox_events` table).

Enables the Transactional Outbox pattern:
Domain mutations and OutboxEvent records are written in the SAME database transaction.
An outbox publisher later reads and dispatches queued events to the EventBus reliably.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class OutboxEventModel(Base):
    """
    SQLAlchemy persistence model for Transactional Outbox events.
    """

    __tablename__ = "outbox_events"
    __table_args__ = (
        Index("ix_outbox_events_status", "status", "occurred_at"),
        Index("ix_outbox_org_id", "organization_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
