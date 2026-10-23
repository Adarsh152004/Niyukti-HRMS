"""
Plan Database Models — SQLAlchemy ORM models for agent_plans and agent_plan_steps.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class PlanModel(Base):
    """SQLAlchemy ORM model for agent_plans table."""

    __tablename__ = "agent_plans"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(64), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(64), ForeignKey("agent_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT", index=True)
    objective: Mapped[str] = mapped_column(String(512), nullable=False)
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)


class PlanStepModel(Base):
    """SQLAlchemy ORM model for agent_plan_steps table."""

    __tablename__ = "agent_plan_steps"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plan_id: Mapped[str] = mapped_column(String(64), ForeignKey("agent_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False, default="TOOL_CALL")
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    command_type: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    arguments_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    dependencies_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    failure_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="LOW")
