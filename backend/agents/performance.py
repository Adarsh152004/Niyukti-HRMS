"""
Agent Framework — Performance Metrics contracts.

Every autonomous HR agent must report performance metrics so the platform
can continuously evaluate agent quality, detect drift, and trigger retraining
or human escalation when thresholds are breached.

Performance thresholds are configurable — no hardcoded "accuracy = good" assumptions.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentPerformanceMetrics(BaseModel):
    """
    Performance metrics snapshot for a single HRMS agent over a measurement period.

    All rates are expressed as floats in [0.0, 1.0].
    All latencies are in seconds.
    All costs are in USD (or configured currency).
    """

    agent_id: str
    agent_role: str
    measurement_period_start: datetime
    measurement_period_end: datetime

    # ── Task Execution ────────────────────────────────────────────────────────
    total_tasks: int = Field(default=0, ge=0)
    successful_tasks: int = Field(default=0, ge=0)
    failed_tasks: int = Field(default=0, ge=0)
    task_success_rate: float = Field(default=0.0, ge=0.0, le=1.0)

    # ── Accuracy & Quality ────────────────────────────────────────────────────
    accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    precision: float | None = Field(default=None, ge=0.0, le=1.0)
    recall: float | None = Field(default=None, ge=0.0, le=1.0)
    f1_score: float | None = Field(default=None, ge=0.0, le=1.0)

    # ── Confidence Calibration ────────────────────────────────────────────────
    mean_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence_calibration_error: float | None = Field(
        default=None,
        description="Expected Calibration Error (ECE). 0.0 = perfectly calibrated.",
    )

    # ── Latency ──────────────────────────────────────────────────────────────
    avg_latency_seconds: float | None = Field(default=None, ge=0.0)
    p95_latency_seconds: float | None = Field(default=None, ge=0.0)
    p99_latency_seconds: float | None = Field(default=None, ge=0.0)

    # ── Cost ─────────────────────────────────────────────────────────────────
    total_cost: float | None = Field(default=None, ge=0.0)
    avg_cost_per_task: float | None = Field(default=None, ge=0.0)

    # ── Human Oversight ───────────────────────────────────────────────────────
    human_override_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of AI decisions that were overridden by humans.",
    )
    escalation_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of tasks that were escalated for human review.",
    )
    recommendation_acceptance_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of AI recommendations accepted by humans.",
    )

    # ── Error & Safety ────────────────────────────────────────────────────────
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    policy_violation_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    false_positive_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    false_negative_rate: float | None = Field(default=None, ge=0.0, le=1.0)

    # ── Outcome Quality ───────────────────────────────────────────────────────
    outcome_quality_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Business-outcome-based quality score, measured post-action.",
    )

    # ── Agent-specific extra metrics ──────────────────────────────────────────
    custom_metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Agent-specific metrics (e.g., resume screening accuracy for ResumeAgent).",
    )

    # ── Metadata ──────────────────────────────────────────────────────────────
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @property
    def reliability_score(self) -> float:
        """
        Composite reliability score combining success rate, error rate, and violation rate.
        Higher is better. Range [0.0, 1.0].
        """
        return max(
            0.0,
            self.task_success_rate - self.error_rate - (self.policy_violation_rate * 2),
        )


class PerformanceThreshold(BaseModel):
    """
    Configurable performance thresholds for a specific agent or agent role.

    When a metric breaches its threshold, the platform may:
    - Alert HR administrators
    - Reduce the agent's autonomy level
    - Trigger retraining
    - Suspend the agent pending review
    """

    agent_role: str
    metric_name: str
    min_value: float | None = Field(default=None)
    max_value: float | None = Field(default=None)
    alert_on_breach: bool = Field(default=True)
    reduce_autonomy_on_breach: bool = Field(default=False)
    suspend_on_breach: bool = Field(default=False)
    description: str = Field(default="")
