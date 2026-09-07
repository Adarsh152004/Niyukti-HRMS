"""
Employee 360 Application Service — Aggregated multi-dimensional profile view.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.employee import Employee
from backend.hrms.ports.repositories import (
    AttendanceRepository,
    DepartmentRepository,
    DesignationRepository,
    EmployeeDocumentRepository,
    EmployeeRepository,
    EmployeeSkillRepository,
    LearningRepository,
    LeaveRepository,
    PerformanceRepository,
)


class Employee360View(BaseModel):
    """Unified 360-degree composite employee operational profile."""

    employee: Employee
    department_name: str | None = None
    designation_title: str | None = None
    manager_name: str | None = None
    skills: list[dict[str, Any]] = Field(default_factory=list)
    documents: list[dict[str, Any]] = Field(default_factory=list)
    recent_attendance: list[dict[str, Any]] = Field(default_factory=list)
    leaves: list[dict[str, Any]] = Field(default_factory=list)
    goals: list[dict[str, Any]] = Field(default_factory=list)
    learning_enrollments: list[dict[str, Any]] = Field(default_factory=list)


class Employee360Service(BaseApplicationService):
    """Consolidates cross-domain HR data into an authoritative Employee 360 view."""

    def __init__(
        self,
        emp_repo: EmployeeRepository,
        dept_repo: DepartmentRepository,
        desig_repo: DesignationRepository,
        skill_repo: EmployeeSkillRepository,
        doc_repo: EmployeeDocumentRepository,
        att_repo: AttendanceRepository,
        leave_repo: LeaveRepository,
        perf_repo: PerformanceRepository,
        learn_repo: LearningRepository,
    ) -> None:
        super().__init__()
        self.emp_repo = emp_repo
        self.dept_repo = dept_repo
        self.desig_repo = desig_repo
        self.skill_repo = skill_repo
        self.doc_repo = doc_repo
        self.att_repo = att_repo
        self.leave_repo = leave_repo
        self.perf_repo = perf_repo
        self.learn_repo = learn_repo

    async def get_employee_360(self, organization_id: str, employee_id: str) -> Employee360View | None:
        """Fetch unified 360 profile across all 15 operational sub-domains."""
        emp = await self.emp_repo.get_by_id(organization_id, employee_id)
        if not emp:
            return None

        # 1. Department & Designation
        dept_name = None
        if emp.department_id:
            dept = await self.dept_repo.get_by_id(organization_id, emp.department_id)
            if dept:
                dept_name = dept.name

        desig_title = None
        if emp.designation_id:
            desig = await self.desig_repo.get_by_id(organization_id, emp.designation_id)
            if desig:
                desig_title = getattr(desig, "title", None) or desig.name

        # 2. Manager
        mgr_name = None
        if emp.manager_id:
            mgr = await self.emp_repo.get_by_id(organization_id, emp.manager_id)
            if mgr:
                mgr_name = f"{mgr.first_name} {mgr.last_name}"

        # 3. Skills
        skills_raw = await self.skill_repo.list_by_employee(organization_id, employee_id)
        skills = [
            {
                "skill_id": s.skill_id,
                "proficiency": s.proficiency.value,
                "years": getattr(s, "years_experience", 0.0),
            }
            for s in skills_raw
        ]

        # 4. Documents
        docs_raw = await self.doc_repo.list_by_employee(organization_id, employee_id)
        documents = [
            {
                "document_id": d.document_id,
                "document_name": d.document_name,
                "type": d.document_type.value,
                "status": d.verification_status.value,
            }
            for d in docs_raw
        ]

        # 5. Attendance (Current Month)
        today = date.today()
        att_raw = await self.att_repo.list_by_employee(
            organization_id, employee_id, start_date=today.replace(day=1), end_date=today
        )
        recent_attendance = [{"date": str(a.date), "status": a.status.value, "work_hours": a.work_hours} for a in att_raw]

        # 6. Leaves
        leaves_raw = await self.leave_repo.list_by_employee(organization_id, employee_id)
        leaves = [
            {"leave_id": lv.leave_id, "type": lv.leave_type.value, "days": lv.total_days, "status": lv.status.value}
            for lv in leaves_raw
        ]

        # 7. Goals
        goals_raw = await self.perf_repo.list_goals(organization_id, employee_id)
        goals = [
            {"goal_id": g.goal_id, "title": g.title, "category": g.category.value, "status": g.status.value} for g in goals_raw
        ]

        # 8. Learning
        learn_raw = await self.learn_repo.list_enrollments(organization_id, employee_id)
        learning = [{"course_id": e.course_id, "status": e.status.value, "progress": e.progress_percentage} for e in learn_raw]

        return Employee360View(
            employee=emp,
            department_name=dept_name,
            designation_title=desig_title,
            manager_name=mgr_name,
            skills=skills,
            documents=documents,
            recent_attendance=recent_attendance,
            leaves=leaves,
            goals=goals,
            learning_enrollments=learning,
        )
