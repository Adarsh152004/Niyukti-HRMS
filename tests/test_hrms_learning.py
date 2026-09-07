"""
Tests for Deterministic Learning LMS Service: Course Catalogs and Enrollments.
"""

from __future__ import annotations

import pytest

from backend.hrms.application.learning_service import LearningService
from backend.hrms.domain.learning import CourseStatus, EnrollmentStatus
from backend.hrms.infrastructure.memory_repositories import InMemoryLearningRepository


@pytest.mark.asyncio
async def test_learning_course_and_enrollment_management():
    repo = InMemoryLearningRepository()
    svc = LearningService(repo)
    org_id = "org-learning-test"
    emp_id = "emp-learn-001"

    # 1. Create course
    course = await svc.create_course(
        organization_id=org_id,
        title="Enterprise Distributed Systems & AI Governance",
        duration_hours=12.5,
        description="Comprehensive architecture guide for distributed systems.",
        category="ENGINEERING",
    )
    assert course.status == CourseStatus.PUBLISHED

    # 2. Enroll employee
    enrollment = await svc.enroll_employee(
        organization_id=org_id,
        course_id=course.course_id,
        employee_id=emp_id,
    )
    assert enrollment.status == EnrollmentStatus.ENROLLED
    assert enrollment.progress_percentage == 0.0

    # 3. List
    courses = await svc.list_courses(org_id)
    enrollments = await svc.list_enrollments(org_id, emp_id)
    assert len(courses) == 1
    assert len(enrollments) == 1
