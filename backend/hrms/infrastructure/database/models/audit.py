"""
SQLAlchemy Models - AuditLog, LoginHistory.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any
from sqlalchemy import String, ForeignKey, Index, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class AuditLogModel(Base):
    """Cryptographic enterprise audit trail for all entity state mutations."""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity", "organization_id", "entity_type", "entity_id"),
        Index("ix_audit_logs_user", "organization_id", "user_id"),
        Index("ix_audit_logs_time", "organization_id", "occurred_at"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(32), default="USER", nullable=False)  # USER, AGENT, SYSTEM
    action: Mapped[str] = mapped_column(String(64), nullable=False)  # CREATE, UPDATE, DELETE, STATUS_CHANGE, LOGIN, EXPORT
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    changes_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)  # {"before": {...}, "after": {...}}
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class LoginHistoryModel(Base):
    """User authentication session security logs."""
    __tablename__ = "login_history"
    __table_args__ = (
        Index("ix_login_history_user", "organization_id", "user_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    logout_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="SUCCESS", nullable=False)  # SUCCESS, FAILED, LOCKED
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
