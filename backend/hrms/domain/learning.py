"""HRMS Domain — TrainingProgram, Course, TrainingEnrollment, CourseEnrollment, Certification, CareerPlan."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field

from backend.hrms.domain.common import HRMSBaseModel, TrainingStatus, generate_id, utc_now


class TrainingMode(StrEnum):
    ONLINE = "ONLINE"
    IN_PERSON = "IN_PERSON"
    HYBRID = "HYBRID"
    SELF_PACED = "SELF_PACED"
    WORKSHOP = "WORKSHOP"
    MENTORSHIP = "MENTORSHIP"


class CourseStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class EnrollmentStatus(StrEnum):
    ENROLLED = "ENROLLED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"


class Course(HRMSBaseModel):
    """A course available to employees."""

    course_id: str = Field(default_factory=generate_id)
    organization_id: str
    title: str
    description: str | None = Field(default=None)
    category: str = "TECHNICAL"
    duration_hours: float = 0.0
    status: CourseStatus = Field(default=CourseStatus.PUBLISHED)
    created_at: datetime = Field(default_factory=utc_now)


class CourseEnrollment(HRMSBaseModel):
    """An employee enrollment in a course."""

    enrollment_id: str = Field(default_factory=generate_id)
    organization_id: str
    course_id: str
    employee_id: str
    status: EnrollmentStatus = Field(default=EnrollmentStatus.ENROLLED)
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    enrolled_at: datetime = Field(default_factory=utc_now)


class TrainingProgram(HRMSBaseModel):
    """A training program available to employees."""

    program_id: str = Field(default_factory=generate_id)
    organization_id: str
    title: str
    description: str | None = Field(default=None)
    skills_covered: list[str] = Field(default_factory=list, description="Skill IDs covered by this program")
    mode: TrainingMode = Field(default=TrainingMode.ONLINE)
    provider: str | None = Field(default=None, description="e.g. 'Coursera', 'Internal'")
    duration_hours: float | None = Field(default=None, ge=0.0)
    cost_per_seat: float | None = Field(default=None, ge=0.0)
    max_participants: int | None = Field(default=None)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    is_mandatory: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_by: str = Field(default="system", description="HR actor who created this program")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class TrainingEnrollment(HRMSBaseModel):
    """An employee's enrollment in a training program."""

    enrollment_id: str = Field(default_factory=generate_id)
    employee_id: str
    program_id: str
    organization_id: str
    enrolled_at: datetime = Field(default_factory=utc_now)
    enrolled_by: str = Field(default="system", description="HR actor or employee who enrolled")
    is_ai_recommended: bool = Field(default=False, description="True if enrollment was AI-recommended")
    ai_recommendation_id: str | None = Field(default=None)
    status: TrainingStatus = Field(default=TrainingStatus.NOT_STARTED)
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    completion_date: date | None = Field(default=None)
    score: float | None = Field(default=None, ge=0.0, le=100.0)
    passed: bool | None = Field(default=None)
    feedback: str | None = Field(default=None)
    certificate_issued: bool = Field(default=False)
    certification_id: str | None = Field(default=None)
    updated_at: datetime = Field(default_factory=utc_now)


class Certification(HRMSBaseModel):
    """A professional certification held by an employee."""

    certification_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    name: str
    issuing_body: str | None = Field(default=None)
    credential_id: str | None = Field(default=None)
    issued_date: date | None = Field(default=None)
    expiry_date: date | None = Field(default=None)
    is_expired: bool = Field(default=False)
    document_key: str | None = Field(default=None, description="Storage key for the certificate document")
    linked_skill_ids: list[str] = Field(default_factory=list)
    verified: bool = Field(default=False)
    verified_by: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)


class CareerPlan(HRMSBaseModel):
    """An employee's career development plan."""

    plan_id: str = Field(default_factory=generate_id)
    employee_id: str
    organization_id: str
    current_designation_id: str
    target_designation_id: str | None = Field(default=None)
    target_timeline_months: int | None = Field(default=None, ge=1)
    current_skills: list[str] = Field(default_factory=list, description="Current skill IDs")
    required_skills: list[str] = Field(default_factory=list, description="Skills needed for target role")
    skill_gaps: list[str] = Field(default_factory=list, description="Gap skill IDs identified by AI")
    recommended_programs: list[str] = Field(default_factory=list, description="Training program IDs recommended")
    milestones: list[dict[str, str]] = Field(default_factory=list)
    is_ai_generated: bool = Field(default=False)
    ai_recommendation_id: str | None = Field(default=None)
    created_by: str = Field(default="system", description="HR/manager who created this plan")
    reviewed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
