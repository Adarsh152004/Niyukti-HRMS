"""
Workflow Infrastructure — SQLAlchemy 2.x Persistence Models for Workflow Entities.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, TimestampMixin


class WorkflowDefinitionModel(Base, TimestampMixin):
    """
    SQLAlchemy persistence model for Workflow Definitions (`workflow_definitions` table).
    """

    __tablename__ = "workflow_definitions"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", "version", name="uq_wf_org_name_ver"),
        Index("ix_wf_org_enabled", "organization_id", "enabled"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(32), default="MANUAL", nullable=False)
    trigger_config_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    steps_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class WorkflowStepModel(Base):
    """
    SQLAlchemy model for Workflow Steps (`workflow_steps` table).
    """

    __tablename__ = "workflow_steps"
    __table_args__ = (Index("ix_wf_steps_wf_id", "workflow_id"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False
    )
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    command_type: Mapped[str] = mapped_column(String(128), nullable=False)
    command_payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    dependencies_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    retry_policy_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class WorkflowExecutionModel(Base):
    """
    SQLAlchemy model for Workflow Executions (`workflow_executions` table).
    """

    __tablename__ = "workflow_executions"
    __table_args__ = (
        Index("ix_wf_exec_org_status", "organization_id", "status"),
        Index("ix_wf_exec_corr_id", "correlation_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String(64), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    causation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="READY", nullable=False)
    current_step: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class StepExecutionModel(Base):
    """
    SQLAlchemy model for Step Executions (`workflow_step_executions` table).
    """

    __tablename__ = "workflow_step_executions"
    __table_args__ = (
        UniqueConstraint("execution_id", "step_id", "attempt", name="uq_step_exec_attempt"),
        Index("ix_step_exec_id", "execution_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    execution_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False
    )
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    output_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ScheduledJobModel(Base, TimestampMixin):
    """
    SQLAlchemy model for Scheduled Background Jobs (`scheduled_jobs` table).
    Includes lease locking attributes for worker concurrency control.
    """

    __tablename__ = "scheduled_jobs"
    __table_args__ = (
        Index("ix_sched_jobs_org_status", "organization_id", "status"),
        Index("ix_sched_jobs_lease", "status", "lease_until"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    workflow_id: Mapped[str] = mapped_column(String(64), nullable=False)
    execution_id: Mapped[str] = mapped_column(String(64), nullable=False)
    step_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    priority: Mapped[str] = mapped_column(String(32), default="NORMAL", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="QUEUED", nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class DeadLetterJobModel(Base):
    """
    SQLAlchemy model for Dead Letter Queue Items (`dead_letter_jobs` table).
    """

    __tablename__ = "dead_letter_jobs"
    __table_args__ = (Index("ix_dlq_org_id", "organization_id"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    execution_id: Mapped[str] = mapped_column(String(64), nullable=False)
    workflow_id: Mapped[str] = mapped_column(String(64), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(64), nullable=False)
    failure_reason: Mapped[str] = mapped_column(String(512), nullable=False)
    error_category: Mapped[str] = mapped_column(String(64), default="NON_RETRYABLE", nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
