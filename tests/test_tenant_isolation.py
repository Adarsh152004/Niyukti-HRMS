"""
Security Tests — Tenant Isolation Boundaries.

Critical Requirements:
TEST 1: Organization A cannot access Organization B employee.
TEST 2: Organization A cannot assign Organization B department to employee.
TEST 3: Organization A cannot assign Organization B employee as manager.
"""

import pytest

from backend.hrms.application.services import DepartmentService, EmployeeService, OrganizationService
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.actor import ActorType
from backend.hrms.domain.exceptions import CrossTenantViolation, EmployeeNotFound
from backend.hrms.infrastructure.memory_repositories import (
    InMemoryDepartmentRepository,
    InMemoryDesignationRepository,
    InMemoryEmployeeRepository,
    InMemoryOrganizationRepository,
)


@pytest.fixture
def repos():
    return {
        "org": InMemoryOrganizationRepository(),
        "dept": InMemoryDepartmentRepository(),
        "des": InMemoryDesignationRepository(),
        "emp": InMemoryEmployeeRepository(),
    }


@pytest.fixture
def services(repos):
    org_service = OrganizationService(repos["org"])
    dept_service = DepartmentService(repos["dept"], repos["org"])
    emp_service = EmployeeService(repos["emp"], repos["dept"], repos["des"])
    return {"org": org_service, "dept": dept_service, "emp": emp_service}


@pytest.mark.asyncio
async def test_organization_a_cannot_access_organization_b_employee(services, repos):
    """TEST 1: Organization A cannot access Organization B employee."""
    ctx_a = TenantContext(
        organization_id="org-A", actor_id="admin-A", actor_type=ActorType.HUMAN, permissions={"ALL_PERMISSIONS"}
    )
    ctx_b = TenantContext(
        organization_id="org-B", actor_id="admin-B", actor_type=ActorType.HUMAN, permissions={"ALL_PERMISSIONS"}
    )

    # Setup Org A and Dept A
    await services["dept"].create_department(ctx_a, name="Engineering A", code="ENG-A")
    dept_a_list = await services["dept"].list_departments(ctx_a)
    dept_a_id = dept_a_list[0].department_id

    # Create Designation A
    from backend.hrms.application.services import DesignationService

    des_service = DesignationService(repos["des"], repos["dept"])
    await des_service.create_designation(ctx_a, name="Dev A", code="DEV-A")
    des_a_list = await des_service.list_designations(ctx_a)
    des_a_id = des_a_list[0].designation_id

    # Create Employee in Org A
    emp_a = await services["emp"].create_employee(
        ctx=ctx_a,
        employee_code="EMP-A001",
        first_name="Alice",
        last_name="Smith",
        email="alice@orga.com",
        department_id=dept_a_id,
        designation_id=des_a_id,
        joining_date="2024-01-01",
    )

    # Org B attempts to access Org A employee -> returns EmployeeNotFound or CrossTenantViolation
    with pytest.raises((EmployeeNotFound, CrossTenantViolation)):
        await services["emp"].get_employee(ctx_b, emp_a.employee_id)


@pytest.mark.asyncio
async def test_organization_a_cannot_assign_organization_b_department(services, repos):
    """TEST 2: Organization A cannot assign Organization B department."""
    ctx_a = TenantContext(organization_id="org-A", actor_id="admin-A", permissions={"ALL_PERMISSIONS"})
    ctx_b = TenantContext(organization_id="org-B", actor_id="admin-B", permissions={"ALL_PERMISSIONS"})

    # Create Dept B in Org B
    await services["dept"].create_department(ctx_b, name="Engineering B", code="ENG-B")
    dept_b_list = await services["dept"].list_departments(ctx_b)
    dept_b_id = dept_b_list[0].department_id

    # Create Des A in Org A
    from backend.hrms.application.services import DesignationService

    des_service = DesignationService(repos["des"], repos["dept"])
    await des_service.create_designation(ctx_a, name="Dev A", code="DEV-A")
    des_a_list = await des_service.list_designations(ctx_a)
    des_a_id = des_a_list[0].designation_id

    # Org A tries to create Employee using Org B's department_id -> CrossTenantViolation
    with pytest.raises(CrossTenantViolation):
        await services["emp"].create_employee(
            ctx=ctx_a,
            employee_code="EMP-A002",
            first_name="Bob",
            last_name="Jones",
            email="bob@orga.com",
            department_id=dept_b_id,
            designation_id=des_a_id,
            joining_date="2024-01-01",
        )


@pytest.mark.asyncio
async def test_organization_a_cannot_assign_organization_b_manager(services, repos):
    """TEST 3: Organization A cannot assign Organization B employee as manager."""
    ctx_a = TenantContext(organization_id="org-A", actor_id="admin-A", permissions={"ALL_PERMISSIONS"})
    ctx_b = TenantContext(organization_id="org-B", actor_id="admin-B", permissions={"ALL_PERMISSIONS"})

    # Create Dept A & Des A in Org A
    await services["dept"].create_department(ctx_a, name="Engineering A", code="ENG-A")
    dept_a_id = (await services["dept"].list_departments(ctx_a))[0].department_id

    from backend.hrms.application.services import DesignationService

    des_service = DesignationService(repos["des"], repos["dept"])
    await des_service.create_designation(ctx_a, name="Dev A", code="DEV-A")
    des_a_id = (await des_service.list_designations(ctx_a))[0].designation_id

    # Create Manager in Org B
    await services["dept"].create_department(ctx_b, name="Engineering B", code="ENG-B")
    dept_b_id = (await services["dept"].list_departments(ctx_b))[0].department_id

    await des_service.create_designation(ctx_b, name="Manager B", code="MGR-B")
    des_b_id = (await des_service.list_designations(ctx_b))[0].designation_id

    mgr_b = await services["emp"].create_employee(
        ctx=ctx_b,
        employee_code="MGR-B001",
        first_name="Boss",
        last_name="Man",
        email="boss@orgb.com",
        department_id=dept_b_id,
        designation_id=des_b_id,
        joining_date="2023-01-01",
    )

    # Org A tries to create Employee with Org B's manager_id -> CrossTenantViolation
    with pytest.raises(CrossTenantViolation):
        await services["emp"].create_employee(
            ctx=ctx_a,
            employee_code="EMP-A003",
            first_name="Charlie",
            last_name="Brown",
            email="charlie@orga.com",
            department_id=dept_a_id,
            designation_id=des_a_id,
            joining_date="2024-01-01",
            manager_id=mgr_b.employee_id,
        )
