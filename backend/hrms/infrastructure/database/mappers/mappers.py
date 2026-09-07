"""
Domain ↕ Database Mappers.

Provides bi-directional, deterministic conversion between Pydantic domain entities
and SQLAlchemy persistence models.

Rule: SQLAlchemy models must NEVER leak into application services.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.hrms.domain.common import Gender
from backend.hrms.domain.documents import DocumentType, EmployeeDocument, VerificationStatus
from backend.hrms.domain.employee import Employee, EmploymentStatus, EmploymentType
from backend.hrms.domain.organization import (
    Department,
    DepartmentStatus,
    Designation,
    DesignationStatus,
    Organization,
    OrganizationStatus,
)
from backend.hrms.domain.role import Role, RoleStatus
from backend.hrms.domain.skills import EmployeeSkill, Proficiency, Skill, SkillCategory, SkillStatus
from backend.hrms.infrastructure.database.models.department import DepartmentModel
from backend.hrms.infrastructure.database.models.designation import DesignationModel
from backend.hrms.infrastructure.database.models.documents import EmployeeDocumentModel
from backend.hrms.infrastructure.database.models.employee import EmployeeModel
from backend.hrms.infrastructure.database.models.organization import OrganizationModel
from backend.hrms.infrastructure.database.models.role import RoleModel
from backend.hrms.infrastructure.database.models.skills import EmployeeSkillModel, SkillModel


class OrganizationMapper:
    @staticmethod
    def to_domain(model: OrganizationModel) -> Organization:
        now = datetime.now(tz=UTC)
        return Organization(
            organization_id=model.id,
            legal_name=model.legal_name,
            display_name=model.display_name,
            slug=model.slug,
            industry=model.industry,
            country=model.country,
            timezone=model.timezone,
            currency=model.currency,
            status=OrganizationStatus(model.status),
            registration_number=model.registration_number,
            logo_url=model.logo_url,
            website=model.website,
            address=model.address,
            founded_year=model.founded_year,
            employee_count=model.employee_count,
            settings=model.settings or {},
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: Organization) -> OrganizationModel:
        return OrganizationModel(
            id=domain.organization_id,
            legal_name=domain.legal_name,
            display_name=domain.display_name,
            slug=domain.slug,
            industry=domain.industry,
            country=domain.country,
            timezone=domain.timezone,
            currency=domain.currency,
            status=domain.status.value,
            registration_number=domain.registration_number,
            logo_url=domain.logo_url,
            website=domain.website,
            address=domain.address,
            founded_year=domain.founded_year,
            employee_count=domain.employee_count,
            settings=domain.settings,
        )


class DepartmentMapper:
    @staticmethod
    def to_domain(model: DepartmentModel) -> Department:
        now = datetime.now(tz=UTC)
        return Department(
            department_id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            code=model.code,
            description=model.description,
            parent_department_id=model.parent_department_id,
            manager_employee_id=model.manager_employee_id,
            cost_center=model.cost_center,
            location=model.location,
            status=DepartmentStatus(model.status),
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: Department) -> DepartmentModel:
        return DepartmentModel(
            id=domain.department_id,
            organization_id=domain.organization_id,
            name=domain.name,
            code=domain.code,
            description=domain.description,
            parent_department_id=domain.parent_department_id,
            manager_employee_id=domain.manager_employee_id,
            cost_center=domain.cost_center,
            location=domain.location,
            status=domain.status.value if hasattr(domain.status, "value") else str(domain.status),
        )


class DesignationMapper:
    @staticmethod
    def to_domain(model: DesignationModel) -> Designation:
        now = datetime.now(tz=UTC)
        return Designation(
            designation_id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            code=model.code,
            description=model.description,
            level=model.level,
            department_id=model.department_id,
            status=DesignationStatus(model.status),
            min_experience_years=model.min_experience_years,
            is_managerial=model.is_managerial,
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: Designation) -> DesignationModel:
        return DesignationModel(
            id=domain.designation_id,
            organization_id=domain.organization_id,
            name=domain.name,
            code=domain.code,
            description=domain.description,
            level=domain.level,
            department_id=domain.department_id,
            status=domain.status.value if hasattr(domain.status, "value") else str(domain.status),
            min_experience_years=domain.min_experience_years,
            is_managerial=domain.is_managerial,
        )


class RoleMapper:
    @staticmethod
    def to_domain(model: RoleModel) -> Role:
        now = datetime.now(tz=UTC)
        return Role(
            role_id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            code=model.code,
            description=model.description,
            permissions=set(model.permissions or []),
            status=RoleStatus(model.status),
            is_system_role=model.is_system_role,
            metadata=model.metadata_json or {},
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: Role) -> RoleModel:
        return RoleModel(
            id=domain.role_id,
            organization_id=domain.organization_id,
            name=domain.name,
            code=domain.code,
            description=domain.description,
            permissions=list(domain.permissions),
            status=domain.status.value if hasattr(domain.status, "value") else str(domain.status),
            is_system_role=domain.is_system_role,
            metadata_json=domain.metadata,
        )


class EmployeeMapper:
    @staticmethod
    def to_domain(model: EmployeeModel) -> Employee:
        now = datetime.now(tz=UTC)
        return Employee(
            employee_id=model.id,
            organization_id=model.organization_id,
            employee_code=model.employee_code,
            first_name=model.first_name,
            last_name=model.last_name,
            preferred_name=model.preferred_name,
            email=model.email,
            phone=model.phone,
            date_of_birth=model.date_of_birth,
            gender=Gender(model.gender) if model.gender else None,
            department_id=model.department_id,
            designation_id=model.designation_id,
            manager_id=model.manager_id,
            employment_status=EmploymentStatus(model.employment_status),
            employment_type=EmploymentType(model.employment_type),
            joining_date=model.joining_date,
            exit_date=model.exit_date,
            location=model.location,
            timezone=model.timezone,
            metadata=model.metadata_json or {},
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: Employee) -> EmployeeModel:
        return EmployeeModel(
            id=domain.employee_id,
            organization_id=domain.organization_id,
            employee_code=domain.employee_code,
            first_name=domain.first_name,
            last_name=domain.last_name,
            preferred_name=domain.preferred_name,
            email=domain.email,
            phone=domain.phone,
            date_of_birth=domain.date_of_birth,
            gender=domain.gender.value if domain.gender else None,
            department_id=domain.department_id,
            designation_id=domain.designation_id,
            manager_id=domain.manager_id,
            employment_status=domain.employment_status.value,
            employment_type=domain.employment_type.value,
            joining_date=domain.joining_date,
            exit_date=domain.exit_date,
            location=domain.location,
            timezone=domain.timezone,
            metadata_json=domain.metadata,
        )


class SkillMapper:
    @staticmethod
    def to_domain(model: SkillModel) -> Skill:
        now = datetime.now(tz=UTC)
        return Skill(
            skill_id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            category=SkillCategory(model.category),
            description=model.description,
            status=SkillStatus(model.status),
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: Skill) -> SkillModel:
        return SkillModel(
            id=domain.skill_id,
            organization_id=domain.organization_id,
            name=domain.name,
            category=domain.category.value if hasattr(domain.category, "value") else str(domain.category),
            description=domain.description,
            status=domain.status.value if hasattr(domain.status, "value") else str(domain.status),
        )


class EmployeeSkillMapper:
    @staticmethod
    def to_domain(model: EmployeeSkillModel) -> EmployeeSkill:
        now = datetime.now(tz=UTC)
        return EmployeeSkill(
            employee_skill_id=model.id,
            organization_id=model.organization_id,
            employee_id=model.employee_id,
            skill_id=model.skill_id,
            proficiency=Proficiency(model.proficiency),
            years_experience=model.years_experience,
            verified=model.verified,
            verified_by=model.verified_by,
            verified_at=model.verified_at,
            created_at=model.created_at or now,
            updated_at=model.updated_at or now,
        )

    @staticmethod
    def to_model(domain: EmployeeSkill) -> EmployeeSkillModel:
        return EmployeeSkillModel(
            id=domain.employee_skill_id,
            organization_id=domain.organization_id,
            employee_id=domain.employee_id,
            skill_id=domain.skill_id,
            proficiency=domain.proficiency.value,
            years_experience=domain.years_experience,
            verified=domain.verified,
            verified_by=domain.verified_by,
            verified_at=domain.verified_at,
        )


class EmployeeDocumentMapper:
    @staticmethod
    def to_domain(model: EmployeeDocumentModel) -> EmployeeDocument:
        return EmployeeDocument(
            document_id=model.id,
            organization_id=model.organization_id,
            employee_id=model.employee_id,
            document_type=DocumentType(model.document_type),
            document_name=model.document_name,
            storage_reference=model.storage_reference,
            mime_type=model.mime_type,
            size=model.size,
            checksum=model.checksum,
            verification_status=VerificationStatus(model.verification_status),
            uploaded_at=model.uploaded_at,
            verified_at=model.verified_at,
            verified_by=model.verified_by,
            expires_at=model.expires_at,
        )

    @staticmethod
    def to_model(domain: EmployeeDocument) -> EmployeeDocumentModel:
        return EmployeeDocumentModel(
            id=domain.document_id,
            organization_id=domain.organization_id,
            employee_id=domain.employee_id,
            document_type=domain.document_type.value,
            document_name=domain.document_name,
            storage_reference=domain.storage_reference,
            mime_type=domain.mime_type,
            size=domain.size,
            checksum=domain.checksum,
            verification_status=domain.verification_status.value,
            uploaded_at=domain.uploaded_at,
            verified_at=domain.verified_at,
            verified_by=domain.verified_by,
            expires_at=domain.expires_at,
        )
