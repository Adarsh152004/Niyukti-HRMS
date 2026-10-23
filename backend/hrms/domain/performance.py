"""HRMS Domain — PerformanceGoal, Goal, GoalCategory, KPI, PerformanceReview, ReviewCycle, ReviewCycleStatus."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, PerformanceRating, generate_id, utc_now


class GoalStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    CANCELLED = "CANCELLED"


class GoalCategory(StrEnum):
    INDIVIDUAL = "INDIVIDUAL"
    TECHNICAL = "TECHNICAL"
    LEADERSHIP = "LEADERSHIP"
    OPERATIONAL = "OPERATIONAL"
    STRATEGIC = "STRATEGIC"


class ReviewCycleStatus(StrEnum):
    UPCOMING = "UPCOMING"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class ReviewCycle(HRMSBaseModel):
    """An appraisal or evaluation cycle."""

    cycle_id: str = Field(default_factory=generate_id)
    organization_id: str
    name: str
    start_date: date
    end_date: date
    description: str = ""
    status: ReviewCycleStatus = Field(default=ReviewCycleStatus.ACTIVE)
    created_at: datetime = Field(default_factory=utc_now)


class KPIStatus(StrEnum):
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    BEHIND = "BEHIND"
    ACHIEVED = "ACHIEVED"
    EXCEEDED = "EXCEEDED"


class ReviewStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    SELF_REVIEW_PENDING = "SELF_REVIEW_PENDING"
    MANAGER_REVIEW_PENDING = "MANAGER_REVIEW_PENDING"
    HR_REVIEW_PENDING = "HR_REVIEW_PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PerformanceGoal(HRMSBaseModel):
    """An individual performance goal set for an employee."""

    goal_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    department_id: str | None = Field(default=None)
    title: str
    description: str | None = Field(default=None)
    category: GoalCategory = Field(default=GoalCategory.INDIVIDUAL)
    goal_type: str = Field(default="INDIVIDUAL", description="'INDIVIDUAL', 'TEAM', 'DEPT'")
    target_metric: str | None = Field(default=None)
    target_value: float | None = Field(default=None)
    actual_value: float | None = Field(default=None)
    unit: str | None = Field(default=None, description="e.g. '% ', 'count', 'INR'")
    weightage: float = Field(default=1.0, ge=0.0, description="Weight in the overall performance score")
    weight: float = Field(default=1.0, ge=0.0, description="Weight in the overall performance score")
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    status: GoalStatus = Field(default=GoalStatus.ACTIVE)
    set_by: str = Field(default="manager", description="Employee/manager who set the goal")
    review_cycle: str | None = Field(default=None, description="e.g. 'Q1-2024'")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


Goal = PerformanceGoal


class KPI(HRMSBaseModel):
    """A Key Performance Indicator associated with an employee or department."""

    kpi_id: str = Field(default_factory=generate_id)
    employee_id: str | None = Field(default=None)
    department_id: str | None = Field(default=None)
    organization_id: str
    name: str
    description: str | None = Field(default=None)
    target_value: float
    actual_value: float | None = Field(default=None)
    unit: str | None = Field(default=None)
    measurement_period: str = Field(description="e.g. 'Q1-2024', '2024-01'")
    status: KPIStatus = Field(default=KPIStatus.ON_TRACK)
    achievement_percentage: float | None = Field(default=None, ge=0.0)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PerformanceReview(HRMSBaseModel):
    """
    A structured performance review for an employee.
    [PII:SENSITIVE] rating, self_rating fields.
    """

    review_id: str = Field(default_factory=generate_id)
    employee_id: str
    reviewer_id: str = Field(description="Manager conducting the review")
    organization_id: str
    review_cycle: str = Field(description="e.g. 'H1-2024', 'Annual-2024'")
    review_period_start: date
    review_period_end: date
    status: ReviewStatus = Field(default=ReviewStatus.SCHEDULED)

    # Self-assessment
    self_rating: PerformanceRating | None = Field(default=None, description="[PII:SENSITIVE] Employee's self-rating")
    self_comments: str | None = Field(default=None)
    self_submitted_at: datetime | None = Field(default=None)

    # Manager assessment
    manager_rating: PerformanceRating | None = Field(default=None, description="[PII:SENSITIVE] Manager's rating")
    manager_comments: str | None = Field(default=None)
    manager_submitted_at: datetime | None = Field(default=None)

    # HR finalization
    final_rating: PerformanceRating | None = Field(default=None, description="[PII:SENSITIVE] Final agreed rating")
    hr_comments: str | None = Field(default=None)
    finalized_by: str | None = Field(default=None)
    finalized_at: datetime | None = Field(default=None)

    # AI prediction
    ai_predicted_rating: PerformanceRating | None = Field(default=None, description="AI-predicted rating from PerformanceAgent")
    ai_prediction_decision_id: str | None = Field(default=None)

    # Promotion consideration
    promotion_recommended: bool = Field(default=False)
    promotion_recommendation_reason: str | None = Field(default=None)

    goals_reviewed: list[str] = Field(default_factory=list, description="List of PerformanceGoal IDs reviewed")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
