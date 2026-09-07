"""
Security Tests — Authorization & AI Agent Permissions.

Critical Requirements:
TEST 4: Employee salary / sensitive data cannot be returned to unauthorized actor.
TEST 5: AI_AGENT without permission cannot mutate employee data.
"""

import pytest

from backend.hrms.application.authorization import AuthorizationService, HRMSAction
from backend.hrms.application.services import EmployeeService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.actor import Actor, ActorType
from backend.hrms.domain.employee import EmploymentStatus
from backend.hrms.domain.exceptions import UnauthorizedAction
from backend.hrms.infrastructure.memory_repositories import (
    InMemoryDepartmentRepository,
    InMemoryDesignationRepository,
    InMemoryEmployeeRepository,
)


@pytest.mark.asyncio
async def test_unauthorized_actor_cannot_view_salary():
    """TEST 4: Employee salary cannot be returned to unauthorized actor."""
    auth = AuthorizationService()

    unauthorized_employee = Actor(
        actor_id="emp-123",
        actor_type=ActorType.HUMAN,
        organization_id="org-A",
        identity="regular.employee@orga.com",
        roles={"EMPLOYEE"},
        permissions={"EMPLOYEE_READ"},  # Basic read permission only, NOT EMPLOYEE_VIEW_SALARY
    )

    authorized_hr_admin = Actor(
        actor_id="hr-456",
        actor_type=ActorType.HUMAN,
        organization_id="org-A",
        identity="hr.admin@orga.com",
        roles={"HR_ADMIN"},
        permissions={"EMPLOYEE_READ", "EMPLOYEE_VIEW_SALARY"},
    )

    # Unauthorized employee check
    assert not auth.can(unauthorized_employee, HRMSAction.EMPLOYEE_VIEW_SALARY, "org-A")

    # Authorized HR admin check
    assert auth.can(authorized_hr_admin, HRMSAction.EMPLOYEE_VIEW_SALARY, "org-A")

    # Enforcement test
    with pytest.raises(UnauthorizedAction):
        auth.enforce(unauthorized_employee, HRMSAction.EMPLOYEE_VIEW_SALARY, "org-A")


@pytest.mark.asyncio
async def test_ai_agent_without_permission_cannot_mutate_employee_data():
    """TEST 5: AI_AGENT without permission cannot mutate employee data."""
    dept_repo = InMemoryDepartmentRepository()
    des_repo = InMemoryDesignationRepository()
    emp_repo = InMemoryEmployeeRepository()
    emp_service = EmployeeService(emp_repo, dept_repo, des_repo)

    # Setup org, dept, des and an active employee
    ctx_setup = TenantContext(organization_id="org-A", actor_id="admin", permissions={"ALL_PERMISSIONS"})
    await dept_repo.create(
        __import__("backend.hrms.domain.organization", fromlist=["Department"]).Department(
            department_id="dept-1", organization_id="org-A", name="Engineering", code="ENG"
        )
    )
    await des_repo.create(
        __import__("backend.hrms.domain.organization", fromlist=["Designation"]).Designation(
            designation_id="des-1", organization_id="org-A", name="Dev", code="DEV"
        )
    )

    emp = await emp_service.create_employee(
        ctx=ctx_setup,
        employee_code="EMP-001",
        first_name="Dave",
        last_name="Miller",
        email="dave@orga.com",
        department_id="dept-1",
        designation_id="des-1",
        joining_date="2024-01-01",
    )

    # AI Agent context WITHOUT EMPLOYEE_UPDATE permission (only READ permission)
    ctx_ai_read_only = TenantContext(
        organization_id="org-A",
        actor_id="resume-screening-agent",
        actor_type=ActorType.AI_AGENT,
        roles={"AI_AGENT"},
        permissions={"EMPLOYEE_READ"},  # NO EMPLOYEE_UPDATE permission
    )

    # AI Agent attempts to terminate employee -> UnauthorizedAction
    with pytest.raises(UnauthorizedAction):
        await emp_service.update_employee_status(ctx_ai_read_only, emp.employee_id, EmploymentStatus.TERMINATED)

    # Verify employee status remains untouched (ACTIVE)
    unchanged_emp = await emp_service.get_employee(ctx_setup, emp.employee_id)
    assert unchanged_emp.employment_status == EmploymentStatus.ACTIVE
