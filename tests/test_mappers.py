"""Tests — Domain ↕ Database Mappers bi-directional conversion."""

from datetime import UTC, date, datetime

from backend.hrms.domain.documents import DocumentType, EmployeeDocument, VerificationStatus
from backend.hrms.domain.employee import Employee, EmploymentStatus, EmploymentType
from backend.hrms.domain.organization import Department, Designation, Organization, OrganizationStatus
from backend.hrms.domain.role import Role
from backend.hrms.domain.skills import EmployeeSkill, Proficiency, Skill, SkillCategory
from backend.hrms.infrastructure.database.mappers.mappers import (
    DepartmentMapper,
    DesignationMapper,
    EmployeeDocumentMapper,
    EmployeeMapper,
    EmployeeSkillMapper,
    OrganizationMapper,
    RoleMapper,
    SkillMapper,
)


def test_organization_mapper_roundtrip():
    domain_org = Organization(
        organization_id="org-100",
        legal_name="Acme Tech Solutions Pvt Ltd",
        display_name="Acme Tech",
        slug="acme-tech",
        industry="Technology",
        country="IN",
        timezone="Asia/Kolkata",
        currency="INR",
        status=OrganizationStatus.ACTIVE,
    )
    model = OrganizationMapper.to_model(domain_org)
    assert model.id == "org-100"
    assert model.slug == "acme-tech"
    assert model.status == "ACTIVE"

    reconverted = OrganizationMapper.to_domain(model)
    assert reconverted.organization_id == domain_org.organization_id
    assert reconverted.legal_name == domain_org.legal_name
    assert reconverted.slug == domain_org.slug
    assert reconverted.status == OrganizationStatus.ACTIVE


def test_department_mapper_roundtrip():
    dept = Department(
        department_id="dept-100",
        organization_id="org-100",
        name="Engineering",
        code="ENG",
        description="Core engineering team",
    )
    model = DepartmentMapper.to_model(dept)
    assert model.id == "dept-100"
    assert model.code == "ENG"

    reconverted = DepartmentMapper.to_domain(model)
    assert reconverted.department_id == dept.department_id
    assert reconverted.code == "ENG"


def test_designation_mapper_roundtrip():
    des = Designation(
        designation_id="des-100",
        organization_id="org-100",
        name="Lead Engineer",
        code="LE",
        level=4,
        is_managerial=True,
    )
    model = DesignationMapper.to_model(des)
    assert model.id == "des-100"
    assert model.is_managerial is True

    reconverted = DesignationMapper.to_domain(model)
    assert reconverted.designation_id == des.designation_id
    assert reconverted.is_managerial is True


def test_role_mapper_roundtrip():
    role = Role(
        role_id="role-100",
        organization_id="org-100",
        name="HR Manager",
        code="HR_MGR",
        permissions={"EMPLOYEE_READ", "EMPLOYEE_CREATE"},
    )
    model = RoleMapper.to_model(role)
    assert model.id == "role-100"
    assert set(model.permissions) == {"EMPLOYEE_READ", "EMPLOYEE_CREATE"}

    reconverted = RoleMapper.to_domain(model)
    assert reconverted.permissions == {"EMPLOYEE_READ", "EMPLOYEE_CREATE"}


def test_employee_mapper_roundtrip():
    emp = Employee(
        employee_id="emp-100",
        organization_id="org-100",
        employee_code="EMP-100",
        first_name="Alice",
        last_name="Smith",
        email="alice@company.com",
        department_id="dept-100",
        designation_id="des-100",
        joining_date=date(2023, 1, 15),
        employment_status=EmploymentStatus.ACTIVE,
        employment_type=EmploymentType.FULL_TIME,
    )
    model = EmployeeMapper.to_model(emp)
    assert model.id == "emp-100"
    assert model.employment_status == "ACTIVE"

    reconverted = EmployeeMapper.to_domain(model)
    assert reconverted.employee_id == emp.employee_id
    assert reconverted.first_name == "Alice"
    assert reconverted.joining_date == date(2023, 1, 15)


def test_skill_and_employee_skill_mapper_roundtrip():
    skill = Skill(
        skill_id="skill-100",
        organization_id="org-100",
        name="Python",
        category=SkillCategory.TECHNICAL,
    )
    skill_model = SkillMapper.to_model(skill)
    reconverted_skill = SkillMapper.to_domain(skill_model)
    assert reconverted_skill.name == "Python"

    emp_skill = EmployeeSkill(
        employee_skill_id="es-100",
        organization_id="org-100",
        employee_id="emp-100",
        skill_id="skill-100",
        proficiency=Proficiency.ADVANCED,
        years_experience=5.5,
    )
    emp_skill_model = EmployeeSkillMapper.to_model(emp_skill)
    reconverted_emp_skill = EmployeeSkillMapper.to_domain(emp_skill_model)
    assert reconverted_emp_skill.proficiency == Proficiency.ADVANCED
    assert reconverted_emp_skill.years_experience == 5.5


def test_document_mapper_roundtrip():
    now = datetime.now(tz=UTC)
    doc = EmployeeDocument(
        document_id="doc-100",
        organization_id="org-100",
        employee_id="emp-100",
        document_type=DocumentType.OFFER_LETTER,
        document_name="Offer_Letter.pdf",
        storage_reference="s3://buckets/offer.pdf",
        size=1024,
        verification_status=VerificationStatus.VERIFIED,
        uploaded_at=now,
    )
    model = EmployeeDocumentMapper.to_model(doc)
    assert model.storage_reference == "s3://buckets/offer.pdf"

    reconverted = EmployeeDocumentMapper.to_domain(model)
    assert reconverted.document_id == "doc-100"
    assert reconverted.document_type == DocumentType.OFFER_LETTER
    assert reconverted.verification_status == VerificationStatus.VERIFIED
