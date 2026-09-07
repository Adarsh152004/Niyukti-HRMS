"""HRMS Domain — Recruitment: Job, JobPosting, JobRequisition, RequisitionStatus, Candidate, CandidateSource, JobApplication, Interview."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from backend.hrms.domain.common import (
    CandidateStatus,
    HRMSBaseModel,
    InterviewStatus,
    JobStatus,
    generate_id,
    utc_now,
)


class RequisitionStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class CandidateSource(StrEnum):
    DIRECT_APPLY = "DIRECT_APPLY"
    LINKEDIN = "LINKEDIN"
    CAREERS_PAGE = "CAREERS_PAGE"
    REFERRAL = "REFERRAL"
    AGENCY = "AGENCY"
    SOURCED = "SOURCED"


class JobRequisition(HRMSBaseModel):
    """An internal request to open hiring for a headcount."""

    requisition_id: str = Field(default_factory=generate_id)
    organization_id: str
    title: str
    department_id: str
    headcount: int = 1
    job_description: str = ""
    min_salary: float | None = None
    max_salary: float | None = None
    status: RequisitionStatus = Field(default=RequisitionStatus.APPROVED)
    created_at: datetime = Field(default_factory=utc_now)


class Job(HRMSBaseModel):
    """A job posting / open position."""

    job_id: str = Field(default_factory=generate_id)
    organization_id: str
    department_id: str
    designation_id: str | None = Field(default=None)
    title: str
    description: str
    requirements: str | None = Field(default=None)
    responsibilities: str | None = Field(default=None)
    required_skills: list[str] = Field(
        default_factory=list,
        description="List of skill IDs required for this position",
    )
    preferred_skills: list[str] = Field(default_factory=list)
    min_experience_years: float | None = Field(default=None, ge=0.0)
    max_experience_years: float | None = Field(default=None)
    min_salary: float | None = Field(default=None)
    max_salary: float | None = Field(default=None)
    location: str | None = Field(default=None)
    is_remote: bool = Field(default=False)
    employment_type: str = Field(default="FULL_TIME")
    openings: int = Field(default=1, ge=1)
    status: JobStatus = Field(default=JobStatus.DRAFT)
    posted_by: str = Field(default="hr_admin", description="HR actor who posted this job")
    posted_at: datetime | None = Field(default=None)
    application_deadline: date | None = Field(default=None)
    filled_at: datetime | None = Field(default=None)
    ai_screening_enabled: bool = Field(
        default=True,
        description="Whether AI resume screening is enabled for this job",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


JobPosting = Job


class Candidate(HRMSBaseModel):
    """
    A candidate who has applied or been sourced for a position.

    PII Classification:
        CONFIDENTIAL: full_name, email, phone, resume_content
    """

    candidate_id: str = Field(default_factory=generate_id)
    organization_id: str

    # Identity — CONFIDENTIAL PII
    first_name: str | None = None
    last_name: str | None = None
    full_name: str = Field(default="")
    email: str = Field(description="[PII:CONFIDENTIAL]")
    phone: str | None = Field(default=None, description="[PII:CONFIDENTIAL]")
    linkedin_url: str | None = Field(default=None)

    # Resume
    resume_file_key: str | None = Field(default=None, description="Storage key for the resume file (encrypted)")
    resume_parsed: bool = Field(default=False)
    parsed_skills: list[str] = Field(default_factory=list, description="Skill IDs extracted by AI resume parser")
    years_of_experience: float | None = Field(default=None, ge=0.0)

    # AI Screening
    ai_score: float | None = Field(default=None, ge=0.0, le=1.0)
    ai_rank: int | None = Field(default=None)
    ai_screening_decision_id: str | None = Field(default=None, description="ID of the AIDecision for this candidate's screening")

    # Status
    status: CandidateStatus = Field(default=CandidateStatus.APPLIED)
    source: CandidateSource | str | None = Field(
        default=CandidateSource.DIRECT_APPLY, description="e.g. 'LinkedIn', 'referral', 'portal'"
    )
    referrer_employee_id: str | None = Field(default=None)

    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def model_post_init(self, __context: Any) -> None:
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()


class JobApplication(HRMSBaseModel):
    """Links a Candidate to a specific Job."""

    application_id: str = Field(default_factory=generate_id)
    job_id: str
    candidate_id: str
    organization_id: str
    applied_at: datetime = Field(default_factory=utc_now)
    status: CandidateStatus = Field(default=CandidateStatus.APPLIED)
    cover_letter: str | None = Field(default=None)
    ai_rank_for_job: int | None = Field(default=None)
    ai_score_for_job: float | None = Field(default=None, ge=0.0, le=1.0)
    stage_notes: dict[str, str] = Field(
        default_factory=dict,
        description="Notes per recruitment stage, keyed by stage name",
    )
    rejected_at: datetime | None = Field(default=None)
    rejection_reason: str | None = Field(default=None)
    rejection_ai_decision_id: str | None = Field(default=None)
    hired_at: datetime | None = Field(default=None)
    updated_at: datetime = Field(default_factory=utc_now)


class Interview(HRMSBaseModel):
    """A scheduled interview for a candidate."""

    interview_id: str = Field(default_factory=generate_id)
    application_id: str
    job_id: str
    candidate_id: str
    organization_id: str
    round_number: int = Field(default=1, ge=1)
    interview_type: str = Field(default="TECHNICAL", description="e.g. HR, TECHNICAL, MANAGERIAL")
    scheduled_at: datetime
    duration_minutes: int = Field(default=60, ge=15)
    location: str | None = Field(default=None)
    meeting_link: str | None = Field(default=None)
    interviewers: list[str] = Field(default_factory=list, description="List of employee IDs conducting the interview")
    status: InterviewStatus = Field(default=InterviewStatus.SCHEDULED)
    calendar_event_id: str | None = Field(default=None)
    feedback: str | None = Field(default=None)
    rating: float | None = Field(default=None, ge=1.0, le=5.0)
    outcome: str | None = Field(default=None, description="e.g. 'PASS', 'FAIL', 'HOLD'")
    ai_scheduled: bool = Field(
        default=False,
        description="True if this interview was autonomously scheduled by AI",
    )
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
