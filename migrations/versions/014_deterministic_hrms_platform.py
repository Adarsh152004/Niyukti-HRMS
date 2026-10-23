"""
Alembic Migration 014 — Deterministic Core HRMS Platform Schema.

Revision ID: 014_deterministic_hrms_platform
Revises: 013_specialized_agent_catalog
Create Date: 2026-08-30 12:45:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "014_deterministic_hrms_platform"
down_revision = "013_specialized_agent_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Shifts & Attendance
    op.create_table(
        "hrms_attendance_records",
        sa.Column("attendance_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("employee_id", sa.String(64), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("check_in_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_out_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("work_hours", sa.Float(), nullable=True),
        sa.Column("overtime_hours", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 2. Leaves
    op.create_table(
        "hrms_leave_requests",
        sa.Column("leave_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("employee_id", sa.String(64), nullable=False, index=True),
        sa.Column("leave_type", sa.String(32), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_days", sa.Float(), nullable=False),
        sa.Column("is_half_day", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, index=True),
        sa.Column("approved_by", sa.String(64), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 3. Payroll Components
    op.create_table(
        "hrms_salary_components",
        sa.Column("component_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("component_type", sa.String(32), nullable=False),
        sa.Column("is_fixed", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("percentage_of", sa.String(64), nullable=True),
        sa.Column("percentage_value", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 4. Recruitment Requisitions & Candidates
    op.create_table(
        "hrms_job_requisitions",
        sa.Column("requisition_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("department_id", sa.String(64), nullable=False),
        sa.Column("headcount", sa.Integer(), server_default="1", nullable=False),
        sa.Column("status", sa.String(32), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "hrms_candidates",
        sa.Column("candidate_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("first_name", sa.String(64), nullable=False),
        sa.Column("last_name", sa.String(64), nullable=False),
        sa.Column("email", sa.String(128), nullable=False, index=True),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 5. Performance Reviews & Goals
    op.create_table(
        "hrms_review_cycles",
        sa.Column("cycle_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "hrms_goals",
        sa.Column("goal_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("employee_id", sa.String(64), nullable=False, index=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("weightage", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("status", sa.String(32), server_default="NOT_STARTED", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 6. Learning Courses & Enrollments
    op.create_table(
        "hrms_courses",
        sa.Column("course_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("duration_hours", sa.Float(), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "hrms_course_enrollments",
        sa.Column("enrollment_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("course_id", sa.String(64), nullable=False, index=True),
        sa.Column("employee_id", sa.String(64), nullable=False, index=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("progress_percentage", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 7. Policies & Approvals
    op.create_table(
        "hrms_policies",
        sa.Column("policy_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.String(16), server_default="1.0", nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "hrms_approval_requests",
        sa.Column("approval_id", sa.String(64), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False, index=True),
        sa.Column("approval_type", sa.String(64), nullable=False, index=True),
        sa.Column("requester_id", sa.String(64), nullable=False),
        sa.Column("target_entity_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, index=True),
        sa.Column("risk_level", sa.String(32), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("hrms_approval_requests")
    op.drop_table("hrms_policies")
    op.drop_table("hrms_course_enrollments")
    op.drop_table("hrms_courses")
    op.drop_table("hrms_goals")
    op.drop_table("hrms_review_cycles")
    op.drop_table("hrms_candidates")
    op.drop_table("hrms_job_requisitions")
    op.drop_table("hrms_salary_components")
    op.drop_table("hrms_leave_requests")
    op.drop_table("hrms_attendance_records")
