"""
PostgreSQL Repository Implementations.

Implements all 8 repository ports using SQLAlchemy 2.x AsyncSession and mappers.
Strictly filters queries by `organization_id` to enforce tenant isolation.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.hrms.domain.documents import EmployeeDocument
from backend.hrms.domain.employee import Employee
from backend.hrms.domain.organization import Department, Designation, Organization
from backend.hrms.domain.role import Role
from backend.hrms.domain.skills import EmployeeSkill, Skill
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
from backend.hrms.infrastructure.database.models.department import DepartmentModel
from backend.hrms.infrastructure.database.models.designation import DesignationModel
from backend.hrms.infrastructure.database.models.documents import EmployeeDocumentModel
from backend.hrms.infrastructure.database.models.employee import EmployeeModel
from backend.hrms.infrastructure.database.models.organization import OrganizationModel
from backend.hrms.infrastructure.database.models.role import RoleModel
from backend.hrms.infrastructure.database.models.skills import EmployeeSkillModel, SkillModel
from backend.hrms.ports.repositories import (
    DepartmentRepository,
    DesignationRepository,
    EmployeeDocumentRepository,
    EmployeeRepository,
    EmployeeSkillRepository,
    OrganizationRepository,
    RoleRepository,
    SkillRepository,
)


class PostgresOrganizationRepository(OrganizationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, organization: Organization) -> Organization:
        model = OrganizationMapper.to_model(organization)
        self.session.add(model)
        await self.session.flush()
        return OrganizationMapper.to_domain(model)

    async def get_by_id(self, organization_id: str) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.id == organization_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return OrganizationMapper.to_domain(model) if model else None

    async def get_by_slug(self, slug: str) -> Organization | None:
        stmt = select(OrganizationModel).where(OrganizationModel.slug == slug)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return OrganizationMapper.to_domain(model) if model else None

    async def update(self, organization: Organization) -> Organization:
        model = OrganizationMapper.to_model(organization)
        merged = await self.session.merge(model)
        await self.session.flush()
        return OrganizationMapper.to_domain(merged)

    async def list_all(self) -> Sequence[Organization]:
        stmt = select(OrganizationModel)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [OrganizationMapper.to_domain(m) for m in models]


class PostgresDepartmentRepository(DepartmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, department: Department) -> Department:
        model = DepartmentMapper.to_model(department)
        self.session.add(model)
        await self.session.flush()
        return DepartmentMapper.to_domain(model)

    async def get_by_id(self, organization_id: str, department_id: str) -> Department | None:
        stmt = select(DepartmentModel).where(
            DepartmentModel.id == department_id,
            DepartmentModel.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return DepartmentMapper.to_domain(model) if model else None

    async def get_by_code(self, organization_id: str, code: str) -> Department | None:
        stmt = select(DepartmentModel).where(
            DepartmentModel.organization_id == organization_id,
            DepartmentModel.code == code,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return DepartmentMapper.to_domain(model) if model else None

    async def list_by_organization(self, organization_id: str) -> Sequence[Department]:
        stmt = select(DepartmentModel).where(DepartmentModel.organization_id == organization_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [DepartmentMapper.to_domain(m) for m in models]

    async def update(self, department: Department) -> Department:
        model = DepartmentMapper.to_model(department)
        merged = await self.session.merge(model)
        await self.session.flush()
        return DepartmentMapper.to_domain(merged)


class PostgresDesignationRepository(DesignationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, designation: Designation) -> Designation:
        model = DesignationMapper.to_model(designation)
        self.session.add(model)
        await self.session.flush()
        return DesignationMapper.to_domain(model)

    async def get_by_id(self, organization_id: str, designation_id: str) -> Designation | None:
        stmt = select(DesignationModel).where(
            DesignationModel.id == designation_id,
            DesignationModel.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return DesignationMapper.to_domain(model) if model else None

    async def get_by_code(self, organization_id: str, code: str) -> Designation | None:
        stmt = select(DesignationModel).where(
            DesignationModel.organization_id == organization_id,
            DesignationModel.code == code,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return DesignationMapper.to_domain(model) if model else None

    async def list_by_organization(self, organization_id: str) -> Sequence[Designation]:
        stmt = select(DesignationModel).where(DesignationModel.organization_id == organization_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [DesignationMapper.to_domain(m) for m in models]

    async def update(self, designation: Designation) -> Designation:
        model = DesignationMapper.to_model(designation)
        merged = await self.session.merge(model)
        await self.session.flush()
        return DesignationMapper.to_domain(merged)


class PostgresRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, role: Role) -> Role:
        model = RoleMapper.to_model(role)
        self.session.add(model)
        await self.session.flush()
        return RoleMapper.to_domain(model)

    async def get_by_id(self, organization_id: str, role_id: str) -> Role | None:
        stmt = select(RoleModel).where(
            RoleModel.id == role_id,
            RoleModel.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return RoleMapper.to_domain(model) if model else None

    async def get_by_code(self, organization_id: str, code: str) -> Role | None:
        stmt = select(RoleModel).where(
            RoleModel.organization_id == organization_id,
            RoleModel.code == code,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return RoleMapper.to_domain(model) if model else None

    async def get_by_name(self, organization_id: str, name: str) -> Role | None:
        stmt = select(RoleModel).where(
            RoleModel.organization_id == organization_id,
            RoleModel.name == name,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return RoleMapper.to_domain(model) if model else None

    async def list_by_organization(self, organization_id: str) -> Sequence[Role]:
        stmt = select(RoleModel).where(RoleModel.organization_id == organization_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [RoleMapper.to_domain(m) for m in models]

    async def update(self, role: Role) -> Role:
        model = RoleMapper.to_model(role)
        merged = await self.session.merge(model)
        await self.session.flush()
        return RoleMapper.to_domain(merged)


class PostgresEmployeeRepository(EmployeeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, employee: Employee) -> Employee:
        model = EmployeeMapper.to_model(employee)
        self.session.add(model)
        await self.session.flush()
        return EmployeeMapper.to_domain(model)

    async def get_by_id(self, organization_id: str, employee_id: str) -> Employee | None:
        stmt = select(EmployeeModel).where(
            EmployeeModel.id == employee_id,
            EmployeeModel.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return EmployeeMapper.to_domain(model) if model else None

    async def get_by_code(self, organization_id: str, employee_code: str) -> Employee | None:
        stmt = select(EmployeeModel).where(
            EmployeeModel.organization_id == organization_id,
            EmployeeModel.employee_code == employee_code,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return EmployeeMapper.to_domain(model) if model else None

    async def get_by_email(self, organization_id: str, email: str) -> Employee | None:
        stmt = select(EmployeeModel).where(
            EmployeeModel.organization_id == organization_id,
            EmployeeModel.email == email,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return EmployeeMapper.to_domain(model) if model else None

    async def list_by_organization(
        self,
        organization_id: str,
        department_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Employee]:
        stmt = select(EmployeeModel).where(EmployeeModel.organization_id == organization_id)
        if department_id:
            stmt = stmt.where(EmployeeModel.department_id == department_id)
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [EmployeeMapper.to_domain(m) for m in models]

    async def update(self, employee: Employee) -> Employee:
        model = EmployeeMapper.to_model(employee)
        merged = await self.session.merge(model)
        await self.session.flush()
        return EmployeeMapper.to_domain(merged)


class PostgresSkillRepository(SkillRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, skill: Skill) -> Skill:
        model = SkillMapper.to_model(skill)
        self.session.add(model)
        await self.session.flush()
        return SkillMapper.to_domain(model)

    async def get_by_id(self, organization_id: str, skill_id: str) -> Skill | None:
        stmt = select(SkillModel).where(
            SkillModel.id == skill_id,
            SkillModel.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return SkillMapper.to_domain(model) if model else None

    async def get_by_name(self, organization_id: str, name: str) -> Skill | None:
        stmt = select(SkillModel).where(
            SkillModel.organization_id == organization_id,
            SkillModel.name == name,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return SkillMapper.to_domain(model) if model else None

    async def list_by_organization(self, organization_id: str) -> Sequence[Skill]:
        stmt = select(SkillModel).where(SkillModel.organization_id == organization_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [SkillMapper.to_domain(m) for m in models]

    async def update(self, skill: Skill) -> Skill:
        model = SkillMapper.to_model(skill)
        merged = await self.session.merge(model)
        await self.session.flush()
        return SkillMapper.to_domain(merged)


class PostgresEmployeeSkillRepository(EmployeeSkillRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, employee_skill: EmployeeSkill) -> EmployeeSkill:
        model = EmployeeSkillMapper.to_model(employee_skill)
        self.session.add(model)
        await self.session.flush()
        return EmployeeSkillMapper.to_domain(model)

    async def get_by_id(self, organization_id: str, employee_skill_id: str) -> EmployeeSkill | None:
        stmt = select(EmployeeSkillModel).where(
            EmployeeSkillModel.id == employee_skill_id,
            EmployeeSkillModel.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return EmployeeSkillMapper.to_domain(model) if model else None

    async def get_by_employee_and_skill(self, organization_id: str, employee_id: str, skill_id: str) -> EmployeeSkill | None:
        stmt = select(EmployeeSkillModel).where(
            EmployeeSkillModel.organization_id == organization_id,
            EmployeeSkillModel.employee_id == employee_id,
            EmployeeSkillModel.skill_id == skill_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return EmployeeSkillMapper.to_domain(model) if model else None

    async def list_by_employee(self, organization_id: str, employee_id: str) -> Sequence[EmployeeSkill]:
        stmt = select(EmployeeSkillModel).where(
            EmployeeSkillModel.organization_id == organization_id,
            EmployeeSkillModel.employee_id == employee_id,
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [EmployeeSkillMapper.to_domain(m) for m in models]

    async def update(self, employee_skill: EmployeeSkill) -> EmployeeSkill:
        model = EmployeeSkillMapper.to_model(employee_skill)
        merged = await self.session.merge(model)
        await self.session.flush()
        return EmployeeSkillMapper.to_domain(merged)


class PostgresEmployeeDocumentRepository(EmployeeDocumentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, document: EmployeeDocument) -> EmployeeDocument:
        model = EmployeeDocumentMapper.to_model(document)
        self.session.add(model)
        await self.session.flush()
        return EmployeeDocumentMapper.to_domain(model)

    async def get_by_id(self, organization_id: str, document_id: str) -> EmployeeDocument | None:
        stmt = select(EmployeeDocumentModel).where(
            EmployeeDocumentModel.id == document_id,
            EmployeeDocumentModel.organization_id == organization_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return EmployeeDocumentMapper.to_domain(model) if model else None

    async def list_by_employee(self, organization_id: str, employee_id: str) -> Sequence[EmployeeDocument]:
        stmt = select(EmployeeDocumentModel).where(
            EmployeeDocumentModel.organization_id == organization_id,
            EmployeeDocumentModel.employee_id == employee_id,
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [EmployeeDocumentMapper.to_domain(m) for m in models]

    async def update(self, document: EmployeeDocument) -> EmployeeDocument:
        model = EmployeeDocumentMapper.to_model(document)
        merged = await self.session.merge(model)
        await self.session.flush()
        return EmployeeDocumentMapper.to_domain(merged)
