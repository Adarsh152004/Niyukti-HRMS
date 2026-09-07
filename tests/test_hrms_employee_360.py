"""
Tests for Consolidated Employee 360 Profile Service.
"""

from __future__ import annotations

from datetime import date

import pytest

from backend.hrms.application.employee_360_service import Employee360Service
from backend.hrms.domain.common import Gender, LeaveType
from backend.hrms.domain.employee import Employee, EmploymentStatus, EmploymentType
from backend.hrms.domain.learning import CourseEnrollment, EnrollmentStatus
from backend.hrms.domain.leave import LeaveRequest
from backend.hrms.domain.organization import Department, Designation
from backend.hrms.domain.performance import Goal, GoalCategory
from backend.hrms.domain.skills import EmployeeSkill, Proficiency
from backend.hrms.infrastructure.memory_repositories import (
    InMemoryAttendanceRepository,
    InMemoryDepartmentRepository,
    InMemoryDesignationRepository,
    InMemoryEmployeeDocumentRepository,
    InMemoryEmployeeRepository,
    InMemoryEmployeeSkillRepository,
    InMemoryLearningRepository,
    InMemoryLeaveRepository,
    InMemoryPerformanceRepository,
)


@pytest.mark.asyncio
async def test_employee_360_profile_aggregation():
    emp_repo = InMemoryEmployeeRepository()
    dept_repo = InMemoryDepartmentRepository()
    desig_repo = InMemoryDesignationRepository()
    skill_repo = InMemoryEmployeeSkillRepository()
    doc_repo = InMemoryEmployeeDocumentRepository()
    att_repo = InMemoryAttendanceRepository()
    leave_repo = InMemoryLeaveRepository()
    perf_repo = InMemoryPerformanceRepository()
    learn_repo = InMemoryLearningRepository()

    svc = Employee360Service(
        emp_repo=emp_repo,
        dept_repo=dept_repo,
        desig_repo=desig_repo,
        skill_repo=skill_repo,
        doc_repo=doc_repo,
        att_repo=att_repo,
        leave_repo=leave_repo,
        perf_repo=perf_repo,
        learn_repo=learn_repo,
    )

    org_id = "org-360-test"

    # Setup Department & Designation
    dept = await dept_repo.create(Department(organization_id=org_id, name="AI Research Lab", code="AIRL"))
    desig = await desig_repo.create(Designation(organization_id=org_id, name="Principal AI Architect", code="PAIR"))

    # Setup Employee
    emp = await emp_repo.create(
        Employee(
            organization_id=org_id,
            employee_code="EMP-360-01",
            first_name="Elena",
            last_name="Rostova",
            email="elena.rostova@example.com",
            department_id=dept.department_id,
            designation_id=desig.designation_id,
            gender=Gender.FEMALE,
            date_of_birth=date(1990, 5, 20),
            joining_date=date(2022, 1, 15),
            employment_status=EmploymentStatus.ACTIVE,
            employment_type=EmploymentType.FULL_TIME,
        )
    )

    # Setup Skill, Goal, Leave, Learning
    await skill_repo.create(
        EmployeeSkill(
            organization_id=org_id,
            employee_id=emp.employee_id,
            skill_id="skill-python",
            proficiency=Proficiency.EXPERT,
            years_experience=8.0,
        )
    )
    await perf_repo.create_goal(
        Goal(
            organization_id=org_id,
            employee_id=emp.employee_id,
            title="Publish Agent Governance Framework",
            category=GoalCategory.TECHNICAL,
        )
    )
    await leave_repo.create(
        LeaveRequest(
            organization_id=org_id,
            employee_id=emp.employee_id,
            leave_type=LeaveType.ANNUAL,
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 12),
            total_days=3.0,
        )
    )
    await learn_repo.create_enrollment(
        CourseEnrollment(
            organization_id=org_id,
            course_id="course-agi-01",
            employee_id=emp.employee_id,
            status=EnrollmentStatus.COMPLETED,
            progress_percentage=100.0,
        )
    )

    # Fetch 360 profile
    profile = await svc.get_employee_360(org_id, emp.employee_id)
    assert profile is not None
    assert profile.employee.first_name == "Elena"
    assert profile.department_name == "AI Research Lab"
    assert profile.designation_title == "Principal AI Architect"
    assert len(profile.skills) == 1
    assert len(profile.goals) == 1
    assert len(profile.leaves) == 1
    assert len(profile.learning_enrollments) == 1
