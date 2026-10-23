"""
Agent Infrastructure — SQLAlchemy 2.x Persistence Models for Agent Entities.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, TimestampMixin


class AgentModel(Base, TimestampMixin):
    """
    SQLAlchemy persistence model for AI Agents (`agents` table).
    """

    __tablename__ = "agents"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_agent_org_name"),
        Index("ix_agents_org_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    agent_type: Mapped[str] = mapped_column(String(64), default="CUSTOM_AGENT", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="CREATED", nullable=False)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    capabilities_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    system_instructions_reference: Mapped[str | None] = mapped_column(String(512), nullable=True)
    max_concurrent_tasks: Mapped[int] = mapped_column(Integer, default=5, nullable=False)


class AgentCapabilityModel(Base):
    """
    SQLAlchemy model for Agent Capabilities (`agent_capabilities` table).
    """

    __tablename__ = "agent_capabilities"
    __table_args__ = (Index("ix_agent_caps_agent_id", "agent_id"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(64), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    capability_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    resource: Mapped[str] = mapped_column(String(128), nullable=False)
    actions_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)
    requires_hitl: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AgentTaskModel(Base, TimestampMixin):
    """
    SQLAlchemy model for Agent Tasks (`agent_tasks` table).
    """

    __tablename__ = "agent_tasks"
    __table_args__ = (
        Index("ix_agent_tasks_org_agent", "organization_id", "agent_id"),
        Index("ix_agent_tasks_status", "status"),
        Index("ix_agent_tasks_corr_id", "correlation_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(64), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    parent_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    goal: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), default="", nullable=False)
    priority: Mapped[str] = mapped_column(String(32), default="NORMAL", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="CREATED", nullable=False)
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class AgentTaskEventModel(Base):
    """
    SQLAlchemy model for Agent Task Execution Audit Events (`agent_task_events` table).
    """

    __tablename__ = "agent_task_events"
    __table_args__ = (Index("ix_task_events_task_id", "task_id"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), ForeignKey("agent_tasks.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    details_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
