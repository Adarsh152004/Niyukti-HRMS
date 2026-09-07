"""
Learning Application Service — Course catalogs, skill mapping, and training enrollment tracking.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.learning import Course, CourseEnrollment, CourseStatus, EnrollmentStatus
from backend.hrms.ports.repositories import LearningRepository


class LearningService(BaseApplicationService):
    """Deterministic LMS course and training plan orchestration."""

    def __init__(self, learning_repo: LearningRepository) -> None:
        super().__init__()
        self.repo = learning_repo

    async def create_course(
        self,
        organization_id: str,
        title: str,
        duration_hours: float,
        description: str = "",
        category: str = "TECHNICAL",
    ) -> Course:
        course = Course(
            organization_id=organization_id,
            title=title,
            duration_hours=duration_hours,
            description=description,
            category=category,
            status=CourseStatus.PUBLISHED,
        )
        return await self.repo.create_course(course)

    async def enroll_employee(
        self,
        organization_id: str,
        course_id: str,
        employee_id: str,
    ) -> CourseEnrollment:
        enrollment = CourseEnrollment(
            organization_id=organization_id,
            course_id=course_id,
            employee_id=employee_id,
            status=EnrollmentStatus.ENROLLED,
            progress_percentage=0.0,
        )
        return await self.repo.create_enrollment(enrollment)

    async def list_courses(self, organization_id: str) -> Sequence[Course]:
        return await self.repo.list_courses(organization_id)

    async def list_enrollments(self, organization_id: str, employee_id: str) -> Sequence[CourseEnrollment]:
        return await self.repo.list_enrollments(organization_id, employee_id)
