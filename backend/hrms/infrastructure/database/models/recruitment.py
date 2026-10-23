"""
SQLAlchemy Models - JobOpening, Candidate, Application, Interview, Offer.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Date, DateTime, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.base import Base, TimestampMixin


class JobOpeningModel(Base, TimestampMixin):
    """Job requisitions and position openings."""
    __tablename__ = "job_openings"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_job_opening_code"),
        Index("ix_job_openings_org", "organization_id"),
        Index("ix_job_openings_status", "organization_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    department_id: Mapped[str] = mapped_column(String(64), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    designation_id: Mapped[str] = mapped_column(String(64), ForeignKey("designations.id", ondelete="RESTRICT"), nullable=False)
    description: Mapped[str] = mapped_column(String(2048), nullable=False)
    requirements_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    employment_type: Mapped[str] = mapped_column(String(32), default="FULL_TIME", nullable=False)
    experience_min: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    experience_max: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    salary_range_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_range_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    positions_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    filled_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recruiter_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    priority: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, URGENT
    status: Mapped[str] = mapped_column(String(32), default="OPEN", nullable=False)  # DRAFT, OPEN, ON_HOLD, CLOSED, CANCELLED
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CandidateModel(Base, TimestampMixin):
    """Candidate profiles applying for jobs."""
    __tablename__ = "candidates"
    __table_args__ = (
        Index("ix_candidates_org_email", "organization_id", "email"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_designation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    skills_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    resume_storage_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="WEBSITE", nullable=False)  # REFERRAL, JOB_BOARD, WEBSITE, AGENCY, LINKEDIN
    notes: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    converted_employee_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)


class CandidateApplicationModel(Base, TimestampMixin):
    """Application linking candidate to a job opening."""
    __tablename__ = "candidate_applications"
    __table_args__ = (
        UniqueConstraint("organization_id", "candidate_id", "job_opening_id", name="uq_cand_app"),
        Index("ix_cand_apps_job", "organization_id", "job_opening_id"),
        Index("ix_cand_apps_cand", "organization_id", "candidate_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(String(64), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_opening_id: Mapped[str] = mapped_column(String(64), ForeignKey("job_openings.id", ondelete="CASCADE"), nullable=False)
    stage: Mapped[str] = mapped_column(String(64), default="APPLIED", nullable=False)  # APPLIED, SCREENING, SHORTLISTED, INTERVIEW, OFFER, HIRED, REJECTED
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stage_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    referred_by_employee_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class InterviewModel(Base, TimestampMixin):
    """Interview round schedules."""
    __tablename__ = "interviews"
    __table_args__ = (
        Index("ix_interviews_app", "organization_id", "application_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    application_id: Mapped[str] = mapped_column(String(64), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False)
    interviewer_employee_id: Mapped[str] = mapped_column(String(64), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    interview_type: Mapped[str] = mapped_column(String(64), default="TECHNICAL", nullable=False)  # PHONE, VIDEO, IN_PERSON, TECHNICAL, HR
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    location_or_link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="SCHEDULED", nullable=False)  # SCHEDULED, COMPLETED, CANCELLED, NO_SHOW


class InterviewFeedbackModel(Base, TimestampMixin):
    """Interviewer evaluation and scoring."""
    __tablename__ = "interview_feedbacks"
    __table_args__ = (
        UniqueConstraint("organization_id", "interview_id", name="uq_interview_feedback"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    interview_id: Mapped[str] = mapped_column(String(64), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)  # 1.0 to 5.0
    strengths: Mapped[str | None] = mapped_column(String(512), nullable=True)
    weaknesses: Mapped[str | None] = mapped_column(String(512), nullable=True)
    recommendation: Mapped[str] = mapped_column(String(64), nullable=False)  # STRONG_HIRE, HIRE, NO_HIRE, STRONG_NO_HIRE
    detailed_feedback: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OfferModel(Base, TimestampMixin):
    """Formal employment offers sent to candidates."""
    __tablename__ = "offers"
    __table_args__ = (
        UniqueConstraint("organization_id", "application_id", name="uq_offer_application"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    application_id: Mapped[str] = mapped_column(String(64), ForeignKey("candidate_applications.id", ondelete="CASCADE"), nullable=False)
    designation_id: Mapped[str] = mapped_column(String(64), ForeignKey("designations.id", ondelete="RESTRICT"), nullable=False)
    department_id: Mapped[str] = mapped_column(String(64), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    salary_structure_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ctc_offered: Mapped[float] = mapped_column(Float, nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    offer_letter_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)  # DRAFT, SENT, ACCEPTED, DECLINED, REVOKED
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
