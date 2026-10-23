"""
API Layer — Dependency Injection container and tenant resolution middleware for all 15 operational modules.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Header

from backend.hrms.application.approval_service import ApprovalInboxService
from backend.hrms.application.attendance_service import AttendanceService
from backend.hrms.application.employee_360_service import Employee360Service
from backend.hrms.application.executive_control_service import ExecutiveControlService
from backend.hrms.application.learning_service import LearningService
from backend.hrms.application.leave_service import LeaveService
from backend.hrms.application.payroll_service import PayrollService
from backend.hrms.application.performance_service import PerformanceService
from backend.hrms.application.policy_service import HRPolicyService
from backend.hrms.application.recruitment_service import RecruitmentService
from backend.hrms.application.report_service import ReportingService
from backend.hrms.application.services import (
    DepartmentService,
    DesignationService,
    EmployeeDocumentService,
    EmployeeService,
    OrganizationService,
    SkillService,
)
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.actor import ActorType
import os
from backend.hrms.infrastructure.sqlite_repositories import (
    SqliteEmployeeRepository,
    SqliteDepartmentRepository,
    SqliteDesignationRepository,
    SqliteAttendanceRepository,
    SqliteWorkLogRepository,
)
from backend.hrms.infrastructure.memory_repositories import (
    InMemoryApprovalRepository,
    InMemoryAttendanceRepository,
    InMemoryDepartmentRepository,
    InMemoryDesignationRepository,
    InMemoryEmployeeDocumentRepository,
    InMemoryEmployeeRepository,
    InMemoryEmployeeSkillRepository,
    InMemoryLearningRepository,
    InMemoryLeaveRepository,
    InMemoryOrganizationRepository,
    InMemoryPayrollRepository,
    InMemoryPerformanceRepository,
    InMemoryPolicyRepository,
    InMemoryRecruitmentRepository,
    InMemoryReportRepository,
    InMemoryRoleRepository,
    InMemorySkillRepository,
)

# Global singleton repository instances for memory mode
_ORG_REPO = InMemoryOrganizationRepository()
_DEPT_REPO = SqliteDepartmentRepository()
_DES_REPO = SqliteDesignationRepository()
_ROLE_REPO = InMemoryRoleRepository()
_EMP_REPO = SqliteEmployeeRepository()
_SKILL_REPO = InMemorySkillRepository()
_EMP_SKILL_REPO = InMemoryEmployeeSkillRepository()
_DOC_REPO = InMemoryEmployeeDocumentRepository()
_ATT_REPO = SqliteAttendanceRepository()
_WORK_LOG_REPO = SqliteWorkLogRepository()
_LEAVE_REPO = InMemoryLeaveRepository()
_PAYROLL_REPO = InMemoryPayrollRepository()
_REC_REPO = InMemoryRecruitmentRepository()
_PERF_REPO = InMemoryPerformanceRepository()
_LEARN_REPO = InMemoryLearningRepository()
_POLICY_REPO = InMemoryPolicyRepository()
_APPROVAL_REPO = InMemoryApprovalRepository()
_REPORT_REPO = InMemoryReportRepository()


def get_tenant_context(
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
    x_actor_id: Annotated[str, Header(alias="X-Actor-ID")] = "admin-user",
    x_actor_type: Annotated[str, Header(alias="X-Actor-Type")] = "HUMAN",
    x_actor_permissions: Annotated[str | None, Header(alias="X-Actor-Permissions")] = "ALL_PERMISSIONS",
) -> TenantContext:
    default_org = os.getenv("DEFAULT_ORG_ID", "org-nova-01")
    resolved_tenant = x_tenant_id if (x_tenant_id and x_tenant_id != "default-tenant") else default_org

    permissions_set = set(x_actor_permissions.split(",")) if x_actor_permissions else set()
    try:
        actor_type_enum = ActorType(x_actor_type)
    except ValueError:
        actor_type_enum = ActorType.HUMAN

    return TenantContext(
        organization_id=resolved_tenant,
        actor_id=x_actor_id,
        actor_type=actor_type_enum,
        permissions=permissions_set,
    )


def get_organization_service() -> OrganizationService:
    return OrganizationService(_ORG_REPO)


def get_department_service() -> DepartmentService:
    return DepartmentService(_DEPT_REPO, _ORG_REPO)


def get_designation_service() -> DesignationService:
    return DesignationService(_DES_REPO, _DEPT_REPO)


def get_employee_service() -> EmployeeService:
    return EmployeeService(_EMP_REPO, _DEPT_REPO, _DES_REPO)


def get_skill_service() -> SkillService:
    return SkillService(_SKILL_REPO, _EMP_SKILL_REPO, _EMP_REPO)


def get_employee_document_service() -> EmployeeDocumentService:
    return EmployeeDocumentService(_DOC_REPO, _EMP_REPO)


get_document_service = get_employee_document_service


def get_attendance_service() -> AttendanceService:
    return AttendanceService(_ATT_REPO)


def get_leave_service() -> LeaveService:
    return LeaveService(_LEAVE_REPO)


def get_payroll_service() -> PayrollService:
    return PayrollService(_PAYROLL_REPO)


def get_recruitment_service() -> RecruitmentService:
    return RecruitmentService(_REC_REPO)


def get_performance_service() -> PerformanceService:
    return PerformanceService(_PERF_REPO)


def get_learning_service() -> LearningService:
    return LearningService(_LEARN_REPO)


def get_policy_service() -> HRPolicyService:
    return HRPolicyService(_POLICY_REPO)


def get_approval_service() -> ApprovalInboxService:
    return ApprovalInboxService(_APPROVAL_REPO)


def get_reporting_service() -> ReportingService:
    return ReportingService(_REPORT_REPO, _EMP_REPO)


def get_employee_360_service() -> Employee360Service:
    return Employee360Service(
        emp_repo=_EMP_REPO,
        dept_repo=_DEPT_REPO,
        desig_repo=_DES_REPO,
        skill_repo=_EMP_SKILL_REPO,
        doc_repo=_DOC_REPO,
        att_repo=_ATT_REPO,
        leave_repo=_LEAVE_REPO,
        perf_repo=_PERF_REPO,
        learn_repo=_LEARN_REPO,
    )


def get_executive_control_service() -> ExecutiveControlService:
    return ExecutiveControlService.get_instance()

def get_work_log_repository() -> SqliteWorkLogRepository:
    return _WORK_LOG_REPO
