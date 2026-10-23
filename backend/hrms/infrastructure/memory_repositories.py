"""
Infrastructure — Thread-safe In-Memory Repository Port Implementations for all 15 HRMS modules.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import date

from backend.hrms.domain.approvals import ApprovalRequest, ApprovalStatus
from backend.hrms.domain.attendance import AttendanceRecord
from backend.hrms.domain.documents import EmployeeDocument
from backend.hrms.domain.employee import Employee
from backend.hrms.domain.learning import Course, CourseEnrollment
from backend.hrms.domain.leave import LeaveRequest
from backend.hrms.domain.organization import Department, Designation, Organization
from backend.hrms.domain.payroll import SalaryComponent
from backend.hrms.domain.performance import Goal, ReviewCycle
from backend.hrms.domain.policy import HRPolicy
from backend.hrms.domain.recruitment import Candidate, JobRequisition
from backend.hrms.domain.reports import HRReportDefinition, HRReportExecution
from backend.hrms.domain.role import Role
from backend.hrms.domain.skills import EmployeeSkill, Skill
from backend.hrms.ports.repositories import (
    ApprovalRepository,
    AttendanceRepository,
    DepartmentRepository,
    DesignationRepository,
    EmployeeDocumentRepository,
    EmployeeRepository,
    EmployeeSkillRepository,
    HRPolicyRepository,
    LearningRepository,
    LeaveRepository,
    OrganizationRepository,
    PayrollRepository,
    PerformanceRepository,
    RecruitmentRepository,
    ReportRepository,
    RoleRepository,
    SkillRepository,
)


class InMemoryOrganizationRepository(OrganizationRepository):
    def __init__(self) -> None:
        self._store: dict[str, Organization] = {}
        self._lock = asyncio.Lock()

    async def create(self, organization: Organization) -> Organization:
        async with self._lock:
            self._store[organization.organization_id] = organization.model_copy()
            return organization.model_copy()

    async def get_by_id(self, organization_id: str) -> Organization | None:
        async with self._lock:
            org = self._store.get(organization_id)
            return org.model_copy() if org else None

    async def get_by_slug(self, slug: str) -> Organization | None:
        async with self._lock:
            for org in self._store.values():
                if org.slug == slug:
                    return org.model_copy()
            return None

    async def update(self, organization: Organization) -> Organization:
        async with self._lock:
            self._store[organization.organization_id] = organization.model_copy()
            return organization.model_copy()

    async def list_all(self) -> Sequence[Organization]:
        async with self._lock:
            return [org.model_copy() for org in self._store.values()]


class InMemoryDepartmentRepository(DepartmentRepository):
    def __init__(self) -> None:
        self._store: dict[str, Department] = {}
        self._lock = asyncio.Lock()

    async def create(self, department: Department) -> Department:
        async with self._lock:
            self._store[department.department_id] = department.model_copy()
            return department.model_copy()

    async def get_by_id(self, organization_id: str, department_id: str) -> Department | None:
        async with self._lock:
            dept = self._store.get(department_id)
            if dept and dept.organization_id == organization_id:
                return dept.model_copy()
            return None

    async def get_by_code(self, organization_id: str, code: str) -> Department | None:
        async with self._lock:
            for dept in self._store.values():
                if dept.organization_id == organization_id and dept.code == code:
                    return dept.model_copy()
            return None

    async def list_by_organization(self, organization_id: str) -> Sequence[Department]:
        async with self._lock:
            return [dept.model_copy() for dept in self._store.values() if dept.organization_id == organization_id]

    async def update(self, department: Department) -> Department:
        async with self._lock:
            self._store[department.department_id] = department.model_copy()
            return department.model_copy()


class InMemoryDesignationRepository(DesignationRepository):
    def __init__(self) -> None:
        self._store: dict[str, Designation] = {}
        self._lock = asyncio.Lock()

    async def create(self, designation: Designation) -> Designation:
        async with self._lock:
            self._store[designation.designation_id] = designation.model_copy()
            return designation.model_copy()

    async def get_by_id(self, organization_id: str, designation_id: str) -> Designation | None:
        async with self._lock:
            desig = self._store.get(designation_id)
            if desig and desig.organization_id == organization_id:
                return desig.model_copy()
            return None

    async def get_by_code(self, organization_id: str, code: str) -> Designation | None:
        async with self._lock:
            for desig in self._store.values():
                if desig.organization_id == organization_id and desig.code == code:
                    return desig.model_copy()
            return None

    async def list_by_organization(self, organization_id: str) -> Sequence[Designation]:
        async with self._lock:
            return [desig.model_copy() for desig in self._store.values() if desig.organization_id == organization_id]

    async def update(self, designation: Designation) -> Designation:
        async with self._lock:
            self._store[designation.designation_id] = designation.model_copy()
            return designation.model_copy()


class InMemoryRoleRepository(RoleRepository):
    def __init__(self) -> None:
        self._store: dict[str, Role] = {}
        self._lock = asyncio.Lock()

    async def create(self, role: Role) -> Role:
        async with self._lock:
            self._store[role.role_id] = role.model_copy()
            return role.model_copy()

    async def get_by_id(self, organization_id: str, role_id: str) -> Role | None:
        async with self._lock:
            r = self._store.get(role_id)
            if r and r.organization_id == organization_id:
                return r.model_copy()
            return None

    async def get_by_name(self, organization_id: str, name: str) -> Role | None:
        async with self._lock:
            for r in self._store.values():
                if r.organization_id == organization_id and r.name == name:
                    return r.model_copy()
            return None

    async def list_by_organization(self, organization_id: str) -> Sequence[Role]:
        async with self._lock:
            return [r.model_copy() for r in self._store.values() if r.organization_id == organization_id]


class InMemoryEmployeeRepository(EmployeeRepository):
    def __init__(self) -> None:
        self._store: dict[str, Employee] = {}
        self._lock = asyncio.Lock()

    async def create(self, employee: Employee) -> Employee:
        async with self._lock:
            self._store[employee.employee_id] = employee.model_copy()
            return employee.model_copy()

    async def get_by_id(self, organization_id: str, employee_id: str) -> Employee | None:
        async with self._lock:
            emp = self._store.get(employee_id)
            if emp and emp.organization_id == organization_id:
                return emp.model_copy()
            return None

    async def get_by_code(self, organization_id: str, employee_code: str) -> Employee | None:
        async with self._lock:
            for emp in self._store.values():
                if emp.organization_id == organization_id and emp.employee_code == employee_code:
                    return emp.model_copy()
            return None

    async def get_by_email(self, organization_id: str, email: str) -> Employee | None:
        async with self._lock:
            for emp in self._store.values():
                if emp.organization_id == organization_id and emp.email == email:
                    return emp.model_copy()
            return None

    async def list_by_organization(
        self,
        organization_id: str,
        department_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Employee]:
        async with self._lock:
            results = [
                emp.model_copy()
                for emp in self._store.values()
                if emp.organization_id == organization_id and (department_id is None or emp.department_id == department_id)
            ]
            return results[offset : offset + limit]

    async def update(self, employee: Employee) -> Employee:
        async with self._lock:
            self._store[employee.employee_id] = employee.model_copy()
            return employee.model_copy()


class InMemorySkillRepository(SkillRepository):
    def __init__(self) -> None:
        self._store: dict[str, Skill] = {}
        self._lock = asyncio.Lock()

    async def create(self, skill: Skill) -> Skill:
        async with self._lock:
            self._store[skill.skill_id] = skill.model_copy()
            return skill.model_copy()

    async def get_by_id(self, organization_id: str, skill_id: str) -> Skill | None:
        async with self._lock:
            sk = self._store.get(skill_id)
            if sk and sk.organization_id == organization_id:
                return sk.model_copy()
            return None

    async def get_by_name(self, organization_id: str, name: str) -> Skill | None:
        async with self._lock:
            for sk in self._store.values():
                if sk.organization_id == organization_id and sk.name.lower() == name.lower():
                    return sk.model_copy()
            return None

    async def list_by_organization(self, organization_id: str) -> Sequence[Skill]:
        async with self._lock:
            return [sk.model_copy() for sk in self._store.values() if sk.organization_id == organization_id]

    async def update(self, skill: Skill) -> Skill:
        async with self._lock:
            self._store[skill.skill_id] = skill.model_copy()
            return skill.model_copy()


class InMemoryEmployeeSkillRepository(EmployeeSkillRepository):
    def __init__(self) -> None:
        self._store: dict[str, EmployeeSkill] = {}
        self._lock = asyncio.Lock()

    async def create(self, employee_skill: EmployeeSkill) -> EmployeeSkill:
        async with self._lock:
            self._store[employee_skill.employee_skill_id] = employee_skill.model_copy()
            return employee_skill.model_copy()

    async def get_by_id(self, organization_id: str, employee_skill_id: str) -> EmployeeSkill | None:
        async with self._lock:
            es = self._store.get(employee_skill_id)
            if es and es.organization_id == organization_id:
                return es.model_copy()
            return None

    async def get_by_employee_and_skill(self, organization_id: str, employee_id: str, skill_id: str) -> EmployeeSkill | None:
        async with self._lock:
            for es in self._store.values():
                if es.organization_id == organization_id and es.employee_id == employee_id and es.skill_id == skill_id:
                    return es.model_copy()
            return None

    async def list_by_employee(self, organization_id: str, employee_id: str) -> Sequence[EmployeeSkill]:
        async with self._lock:
            return [
                es.model_copy()
                for es in self._store.values()
                if es.organization_id == organization_id and es.employee_id == employee_id
            ]

    async def update(self, employee_skill: EmployeeSkill) -> EmployeeSkill:
        async with self._lock:
            self._store[employee_skill.employee_skill_id] = employee_skill.model_copy()
            return employee_skill.model_copy()


class InMemoryEmployeeDocumentRepository(EmployeeDocumentRepository):
    def __init__(self) -> None:
        self._store: dict[str, EmployeeDocument] = {}
        self._lock = asyncio.Lock()

    async def create(self, document: EmployeeDocument) -> EmployeeDocument:
        async with self._lock:
            self._store[document.document_id] = document.model_copy()
            return document.model_copy()

    async def get_by_id(self, organization_id: str, document_id: str) -> EmployeeDocument | None:
        async with self._lock:
            doc = self._store.get(document_id)
            if doc and doc.organization_id == organization_id:
                return doc.model_copy()
            return None

    async def list_by_employee(self, organization_id: str, employee_id: str) -> Sequence[EmployeeDocument]:
        async with self._lock:
            return [
                doc.model_copy()
                for doc in self._store.values()
                if doc.organization_id == organization_id and doc.employee_id == employee_id
            ]

    async def update(self, document: EmployeeDocument) -> EmployeeDocument:
        async with self._lock:
            self._store[document.document_id] = document.model_copy()
            return document.model_copy()


class InMemoryAttendanceRepository(AttendanceRepository):
    def __init__(self) -> None:
        self._store: dict[str, AttendanceRecord] = {}
        self._lock = asyncio.Lock()

    async def create_or_update(self, record: AttendanceRecord) -> AttendanceRecord:
        async with self._lock:
            self._store[record.attendance_id] = record.model_copy()
            return record.model_copy()

    async def get_by_employee_and_date(
        self, organization_id: str, employee_id: str, record_date: date
    ) -> AttendanceRecord | None:
        async with self._lock:
            for r in self._store.values():
                if r.organization_id == organization_id and r.employee_id == employee_id and r.date == record_date:
                    return r.model_copy()
            return None

    async def list_by_employee(
        self, organization_id: str, employee_id: str, start_date: date, end_date: date
    ) -> Sequence[AttendanceRecord]:
        async with self._lock:
            return [
                r.model_copy()
                for r in self._store.values()
                if r.organization_id == organization_id and r.employee_id == employee_id and start_date <= r.date <= end_date
            ]


class InMemoryLeaveRepository(LeaveRepository):
    def __init__(self) -> None:
        self._store: dict[str, LeaveRequest] = {}
        self._lock = asyncio.Lock()

    async def create(self, request: LeaveRequest) -> LeaveRequest:
        async with self._lock:
            self._store[request.leave_id] = request.model_copy()
            return request.model_copy()

    async def get_by_id(self, organization_id: str, leave_id: str) -> LeaveRequest | None:
        async with self._lock:
            req = self._store.get(leave_id)
            if req and req.organization_id == organization_id:
                return req.model_copy()
            return None

    async def list_by_employee(self, organization_id: str, employee_id: str) -> Sequence[LeaveRequest]:
        async with self._lock:
            return [
                req.model_copy()
                for req in self._store.values()
                if req.organization_id == organization_id and req.employee_id == employee_id
            ]

    async def update(self, request: LeaveRequest) -> LeaveRequest:
        async with self._lock:
            self._store[request.leave_id] = request.model_copy()
            return request.model_copy()


class InMemoryPayrollRepository(PayrollRepository):
    def __init__(self) -> None:
        self._components: dict[str, SalaryComponent] = {}
        self._lock = asyncio.Lock()

    async def create_component(self, component: SalaryComponent) -> SalaryComponent:
        async with self._lock:
            self._components[component.component_id] = component.model_copy()
            return component.model_copy()

    async def list_components(self, organization_id: str) -> Sequence[SalaryComponent]:
        async with self._lock:
            return [c.model_copy() for c in self._components.values() if c.organization_id == organization_id]


class InMemoryRecruitmentRepository(RecruitmentRepository):
    def __init__(self) -> None:
        self._requisitions: dict[str, JobRequisition] = {}
        self._candidates: dict[str, Candidate] = {}
        self._lock = asyncio.Lock()

    async def create_requisition(self, req: JobRequisition) -> JobRequisition:
        async with self._lock:
            self._requisitions[req.requisition_id] = req.model_copy()
            return req.model_copy()

    async def get_requisition(self, organization_id: str, requisition_id: str) -> JobRequisition | None:
        async with self._lock:
            r = self._requisitions.get(requisition_id)
            if r and r.organization_id == organization_id:
                return r.model_copy()
            return None

    async def list_requisitions(self, organization_id: str) -> Sequence[JobRequisition]:
        async with self._lock:
            return [r.model_copy() for r in self._requisitions.values() if r.organization_id == organization_id]

    async def create_candidate(self, candidate: Candidate) -> Candidate:
        async with self._lock:
            self._candidates[candidate.candidate_id] = candidate.model_copy()
            return candidate.model_copy()

    async def list_candidates(self, organization_id: str) -> Sequence[Candidate]:
        async with self._lock:
            return [c.model_copy() for c in self._candidates.values() if c.organization_id == organization_id]


class InMemoryPerformanceRepository(PerformanceRepository):
    def __init__(self) -> None:
        self._cycles: dict[str, ReviewCycle] = {}
        self._goals: dict[str, Goal] = {}
        self._lock = asyncio.Lock()

    async def create_cycle(self, cycle: ReviewCycle) -> ReviewCycle:
        async with self._lock:
            self._cycles[cycle.cycle_id] = cycle.model_copy()
            return cycle.model_copy()

    async def list_cycles(self, organization_id: str) -> Sequence[ReviewCycle]:
        async with self._lock:
            return [c.model_copy() for c in self._cycles.values() if c.organization_id == organization_id]

    async def create_goal(self, goal: Goal) -> Goal:
        async with self._lock:
            self._goals[goal.goal_id] = goal.model_copy()
            return goal.model_copy()

    async def list_goals(self, organization_id: str, employee_id: str) -> Sequence[Goal]:
        async with self._lock:
            return [
                g.model_copy()
                for g in self._goals.values()
                if g.organization_id == organization_id and g.employee_id == employee_id
            ]


class InMemoryLearningRepository(LearningRepository):
    def __init__(self) -> None:
        self._courses: dict[str, Course] = {}
        self._enrollments: dict[str, CourseEnrollment] = {}
        self._lock = asyncio.Lock()

    async def create_course(self, course: Course) -> Course:
        async with self._lock:
            self._courses[course.course_id] = course.model_copy()
            return course.model_copy()

    async def list_courses(self, organization_id: str) -> Sequence[Course]:
        async with self._lock:
            return [c.model_copy() for c in self._courses.values() if c.organization_id == organization_id]

    async def create_enrollment(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        async with self._lock:
            self._enrollments[enrollment.enrollment_id] = enrollment.model_copy()
            return enrollment.model_copy()

    async def list_enrollments(self, organization_id: str, employee_id: str) -> Sequence[CourseEnrollment]:
        async with self._lock:
            return [
                e.model_copy()
                for e in self._enrollments.values()
                if e.organization_id == organization_id and e.employee_id == employee_id
            ]


class InMemoryPolicyRepository(HRPolicyRepository):
    def __init__(self) -> None:
        self._policies: dict[str, HRPolicy] = {}
        self._lock = asyncio.Lock()

    async def create_policy(self, policy: HRPolicy) -> HRPolicy:
        async with self._lock:
            self._policies[policy.policy_id] = policy.model_copy()
            return policy.model_copy()

    async def get_policy(self, organization_id: str, policy_id: str) -> HRPolicy | None:
        async with self._lock:
            p = self._policies.get(policy_id)
            if p and p.organization_id == organization_id:
                return p.model_copy()
            return None

    async def list_policies(self, organization_id: str) -> Sequence[HRPolicy]:
        async with self._lock:
            return [p.model_copy() for p in self._policies.values() if p.organization_id == organization_id]


class InMemoryApprovalRepository(ApprovalRepository):
    def __init__(self) -> None:
        self._approvals: dict[str, ApprovalRequest] = {}
        self._lock = asyncio.Lock()

    async def create(self, request: ApprovalRequest) -> ApprovalRequest:
        async with self._lock:
            self._approvals[request.approval_id] = request.model_copy()
            return request.model_copy()

    async def get_by_id(self, organization_id: str, approval_id: str) -> ApprovalRequest | None:
        async with self._lock:
            req = self._approvals.get(approval_id)
            if req and req.organization_id == organization_id:
                return req.model_copy()
            return None

    async def list_pending(self, organization_id: str) -> Sequence[ApprovalRequest]:
        async with self._lock:
            return [
                req.model_copy()
                for req in self._approvals.values()
                if req.organization_id == organization_id and req.status == ApprovalStatus.PENDING
            ]

    async def update(self, request: ApprovalRequest) -> ApprovalRequest:
        async with self._lock:
            self._approvals[request.approval_id] = request.model_copy()
            return request.model_copy()


class InMemoryReportRepository(ReportRepository):
    def __init__(self) -> None:
        self._definitions: dict[str, HRReportDefinition] = {}
        self._executions: dict[str, HRReportExecution] = {}
        self._lock = asyncio.Lock()

    async def create_definition(self, definition: HRReportDefinition) -> HRReportDefinition:
        async with self._lock:
            self._definitions[definition.report_id] = definition.model_copy()
            return definition.model_copy()

    async def list_definitions(self, organization_id: str) -> Sequence[HRReportDefinition]:
        async with self._lock:
            return [d.model_copy() for d in self._definitions.values() if d.organization_id == organization_id]

    async def record_execution(self, execution: HRReportExecution) -> HRReportExecution:
        async with self._lock:
            self._executions[execution.execution_id] = execution.model_copy()
            return execution.model_copy()
