"""
Tests — HRMS Domain Application Services.

Tests business workflows, event publication, and domain repository interactions.
"""

import pytest

from backend.hrms.application.services import (
    DepartmentService,
    DesignationService,
    EmployeeDocumentService,
    EmployeeService,
    OrganizationService,
    SkillService,
)
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.documents import DocumentType, VerificationStatus
from backend.hrms.domain.employee import EmploymentStatus
from backend.hrms.domain.skills import Proficiency
from backend.hrms.infrastructure.memory_repositories import (
    InMemoryDepartmentRepository,
    InMemoryDesignationRepository,
    InMemoryEmployeeDocumentRepository,
    InMemoryEmployeeRepository,
    InMemoryEmployeeSkillRepository,
    InMemoryOrganizationRepository,
    InMemorySkillRepository,
)


@pytest.fixture
def ctx():
    return TenantContext(
        organization_id="tenant-acme",
        actor_id="admin-1",
        permissions={"ALL_PERMISSIONS"},
    )


@pytest.fixture
def repos():
    return {
        "org": InMemoryOrganizationRepository(),
        "dept": InMemoryDepartmentRepository(),
        "des": InMemoryDesignationRepository(),
        "emp": InMemoryEmployeeRepository(),
        "skill": InMemorySkillRepository(),
        "emp_skill": InMemoryEmployeeSkillRepository(),
        "doc": InMemoryEmployeeDocumentRepository(),
    }


@pytest.mark.asyncio
async def test_organization_service_lifecycle(ctx, repos):
    service = OrganizationService(repos["org"])
    org = await service.create_organization(
        ctx=ctx,
        legal_name="Acme Corporation Pvt Ltd",
        display_name="Acme Corp",
        slug="acme-corp",
    )
    assert org.organization_id is not None
    assert org.legal_name == "Acme Corporation Pvt Ltd"

    fetched = await service.get_organization(ctx, org.organization_id)
    assert fetched.slug == "acme-corp"


@pytest.mark.asyncio
async def test_department_and_designation_services(ctx, repos):
    dept_service = DepartmentService(repos["dept"], repos["org"])
    des_service = DesignationService(repos["des"], repos["dept"])

    dept = await dept_service.create_department(ctx, name="Engineering", code="ENG")
    assert dept.department_id is not None

    des = await des_service.create_designation(ctx, name="Senior Engineer", code="SSE", level=3, department_id=dept.department_id)
    assert des.designation_id is not None

    depts = await dept_service.list_departments(ctx)
    assert len(depts) == 1

    dess = await des_service.list_designations(ctx)
    assert len(dess) == 1


@pytest.mark.asyncio
async def test_employee_service_full_workflow(ctx, repos):
    dept_service = DepartmentService(repos["dept"], repos["org"])
    des_service = DesignationService(repos["des"], repos["dept"])
    emp_service = EmployeeService(repos["emp"], repos["dept"], repos["des"])

    dept = await dept_service.create_department(ctx, name="HR", code="HR")
    des = await des_service.create_designation(ctx, name="HR Lead", code="HRL")

    emp = await emp_service.create_employee(
        ctx=ctx,
        employee_code="EMP-101",
        first_name="Sarah",
        last_name="Connor",
        email="sarah@acme.com",
        department_id=dept.department_id,
        designation_id=des.designation_id,
        joining_date="2024-01-15",
    )
    assert emp.employee_id is not None
    assert emp.full_name == "Sarah Connor"

    # Status update
    updated = await emp_service.update_employee_status(ctx, emp.employee_id, EmploymentStatus.ON_LEAVE)
    assert updated.employment_status == EmploymentStatus.ON_LEAVE


@pytest.mark.asyncio
async def test_skill_service_workflow(ctx, repos):
    dept_service = DepartmentService(repos["dept"], repos["org"])
    des_service = DesignationService(repos["des"], repos["dept"])
    emp_service = EmployeeService(repos["emp"], repos["dept"], repos["des"])
    skill_service = SkillService(repos["skill"], repos["emp_skill"], repos["emp"])

    dept = await dept_service.create_department(ctx, name="IT", code="IT")
    des = await des_service.create_designation(ctx, name="DevOps Engineer", code="DEVOPS")
    emp = await emp_service.create_employee(
        ctx=ctx,
        employee_code="EMP-200",
        first_name="John",
        last_name="Doe",
        email="john.doe@acme.com",
        department_id=dept.department_id,
        designation_id=des.designation_id,
        joining_date="2024-02-01",
    )

    skill = await skill_service.create_skill(ctx, name="Python", category="TECHNICAL")
    assert skill.skill_id is not None

    emp_skill = await skill_service.add_employee_skill(
        ctx=ctx,
        employee_id=emp.employee_id,
        skill_id=skill.skill_id,
        proficiency=Proficiency.EXPERT,
        years_experience=5.0,
    )
    assert emp_skill.proficiency == Proficiency.EXPERT


@pytest.mark.asyncio
async def test_document_service_workflow(ctx, repos):
    dept_service = DepartmentService(repos["dept"], repos["org"])
    des_service = DesignationService(repos["des"], repos["dept"])
    emp_service = EmployeeService(repos["emp"], repos["dept"], repos["des"])
    doc_service = EmployeeDocumentService(repos["doc"], repos["emp"])

    dept = await dept_service.create_department(ctx, name="Legal", code="LEG")
    des = await des_service.create_designation(ctx, name="Counsel", code="CNSL")
    emp = await emp_service.create_employee(
        ctx=ctx,
        employee_code="EMP-300",
        first_name="Mike",
        last_name="Ross",
        email="mike@acme.com",
        department_id=dept.department_id,
        designation_id=des.designation_id,
        joining_date="2024-03-01",
    )

    doc = await doc_service.upload_document_metadata(
        ctx=ctx,
        employee_id=emp.employee_id,
        document_type=DocumentType.OFFER_LETTER,
        document_name="Offer_Letter_Mike.pdf",
        storage_reference="s3://acme-bucket/docs/offer-mike.pdf",
        size=102450,
    )
    assert doc.document_id is not None
    assert doc.verification_status == VerificationStatus.UNVERIFIED

    verified = await doc_service.verify_document(ctx, doc.document_id)
    assert verified.verification_status == VerificationStatus.VERIFIED
    assert verified.verified_by == ctx.actor_id
