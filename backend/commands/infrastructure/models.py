"""
Command Infrastructure — SQLAlchemy 2.x Persistence Models for Command Execution.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, TimestampMixin


class CommandModel(Base, TimestampMixin):
    """
    SQLAlchemy persistence model for Commands (`commands` table).
    """

    __tablename__ = "commands"
    __table_args__ = (
        Index("ix_cmd_org_type", "organization_id", "command_type"),
        UniqueConstraint("organization_id", "idempotency_key", name="uq_cmd_org_idempotency"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    command_type: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), default="WEB", nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="RECEIVED", nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)


class CommandExecutionModel(Base):
    """
    SQLAlchemy model for Command Executions (`command_executions` table).
    """

    __tablename__ = "command_executions"
    __table_args__ = (Index("ix_cmd_exec_cmd_id", "command_id"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    command_id: Mapped[str] = mapped_column(String(64), ForeignKey("commands.id", ondelete="CASCADE"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(primary_key=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    executor: Mapped[str] = mapped_column(String(64), nullable=False)


class CommandApprovalModel(Base, TimestampMixin):
    """
    SQLAlchemy model for Command Approvals (`command_approvals` table).
    """

    __tablename__ = "command_approvals"
    __table_args__ = (Index("ix_cmd_appr_org_status", "organization_id", "status"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    command_id: Mapped[str] = mapped_column(String(64), ForeignKey("commands.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_by_actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    approver_actor_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
