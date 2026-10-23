"""
Delegation Database Models — SQLAlchemy 2.x ORM models for Multi-Agent Delegation tables.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class DelegationModel(Base):
    """SQLAlchemy ORM model for agent_delegations table."""

    __tablename__ = "agent_delegations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    delegator_agent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    delegate_agent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    parent_task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    delegated_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    capabilities_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    scope: Mapped[str] = mapped_column(String(32), nullable=False, default="TASK_SCOPED")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="REQUESTED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    parent_delegation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    allow_further_delegation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    payload_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class DelegatedTaskModel(Base):
    """SQLAlchemy ORM model for agent_delegated_tasks table."""

    __tablename__ = "agent_delegated_tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    delegation_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("agent_delegations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    delegator_agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    delegate_agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    goal: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
