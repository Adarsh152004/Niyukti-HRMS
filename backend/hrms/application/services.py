"""
Application Layer Services — Core HRMS Business Orchestration.

Services handle:
- Domain validation & cross-tenant reference checks
- Capability-oriented authorization enforcement
- Tenant context resolution
- Repository persistence
- Audit-ready domain event creation

Business logic lives HERE, never in FastAPI route handlers or UI components.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from backend.hrms.application.authorization import AuthorizationService, HRMSAction
from backend.hrms.application.tenant_context import TenantContext
from backend.hrms.domain.common import utc_now
from backend.hrms.domain.documents import DocumentType, EmployeeDocument, VerificationStatus
from backend.hrms.domain.employee import Employee, EmploymentStatus, EmploymentType
from backend.hrms.domain.events import (
    DepartmentCreated,
    DesignationCreated,
    DomainEvent,
    EmployeeCreated,
    EmployeeDocumentUploaded,
    EmployeeDocumentVerified,
    EmployeeResigned,
    EmployeeSkillAdded,
    EmployeeTerminated,
    EmployeeUpdated,
    OrganizationCreated,
)
from backend.hrms.domain.exceptions import (
    CrossTenantViolation,
    DocumentNotFound,
    DuplicateEmployeeCode,
    EmployeeNotFound,
    InvalidSkill,
    OrganizationNotFound,
)
from backend.hrms.domain.organization import Department, Designation, Organization, OrganizationStatus
from backend.hrms.domain.skills import EmployeeSkill, Proficiency, Skill, SkillCategory
from backend.hrms.ports.repositories import (
    DepartmentRepository,
    DesignationRepository,
    EmployeeDocumentRepository,
    EmployeeRepository,
    EmployeeSkillRepository,
    OrganizationRepository,
    SkillRepository,
)
from backend.runtime.events import Event, EventBus


class BaseApplicationService:
    def __init__(self, auth_service: AuthorizationService | None = None, event_bus: EventBus | None = None) -> None:
        self.auth = auth_service or AuthorizationService()
        self.event_bus = event_bus or EventBus.get_instance()

    async def _publish(self, domain_event: DomainEvent, actor_id: str) -> None:
        evt = Event(
            event_type=domain_event.event_type,
            source=actor_id,
            payload=domain_event.model_dump(),
        )
        await self.event_bus.publish(evt)


class OrganizationService(BaseApplicationService):
    def __init__(
        self,
        org_repo: OrganizationRepository,
        auth_service: AuthorizationService | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        super().__init__(auth_service, event_bus)
        self.org_repo = org_repo

    async def create_organization(
        self,
        ctx: TenantContext,
        legal_name: str,
        display_name: str,
        slug: str,
        industry: str | None = None,
        country: str = "IN",
        timezone: str = "Asia/Kolkata",
        currency: str = "INR",
    ) -> Organization:
        actor = ctx.to_actor("OrganizationService.create_organization")

        org = Organization(
            legal_name=legal_name,
            display_name=display_name,
            slug=slug,
            industry=industry,
            country=country,
            timezone=timezone,
            currency=currency,
            status=OrganizationStatus.ACTIVE,
        )
        saved = await self.org_repo.create(org)

        event = OrganizationCreated(
            organization_id=saved.organization_id,
            aggregate_id=saved.organization_id,
            actor=actor.model_dump(),
            metadata={"slug": slug, "legal_name": legal_name},
        )
        await self._publish(event, actor.actor_id)
        return saved

    async def get_organization(self, ctx: TenantContext, organization_id: str) -> Organization:
        actor = ctx.to_actor("OrganizationService.get_organization")
        self.auth.enforce(actor, HRMSAction.ORGANIZATION_READ, organization_id)

        org = await self.org_repo.get_by_id(organization_id)
        if not org:
            raise OrganizationNotFound(organization_id)
        return org


class DepartmentService(BaseApplicationService):
    def __init__(
        self,
        dept_repo: DepartmentRepository,
        org_repo: OrganizationRepository,
        auth_service: AuthorizationService | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        super().__init__(auth_service, event_bus)
        self.dept_repo = dept_repo
        self.org_repo = org_repo

    async def create_department(
        self,
        ctx: TenantContext,
        name: str,
        code: str,
        description: str | None = None,
        manager_employee_id: str | None = None,
        parent_department_id: str | None = None,
    ) -> Department:
        actor = ctx.to_actor("DepartmentService.create_department")
        self.auth.enforce(actor, HRMSAction.DEPARTMENT_CREATE, ctx.organization_id)

        if parent_department_id:
            parent = await self.dept_repo.get_by_id(ctx.organization_id, parent_department_id)
            if not parent or parent.organization_id != ctx.organization_id:
                raise CrossTenantViolation("Department", parent_department_id, ctx.organization_id)

        dept = Department(
            organization_id=ctx.organization_id,
            name=name,
            code=code,
            description=description,
            manager_employee_id=manager_employee_id,
            parent_department_id=parent_department_id,
        )
        saved = await self.dept_repo.create(dept)

        event = DepartmentCreated(
            organization_id=ctx.organization_id,
            aggregate_id=saved.department_id,
            actor=actor.model_dump(),
            metadata={"name": name, "code": code},
        )
        await self._publish(event, actor.actor_id)
        return saved

    async def list_departments(self, ctx: TenantContext) -> Sequence[Department]:
        actor = ctx.to_actor("DepartmentService.list_departments")
        self.auth.enforce(actor, HRMSAction.DEPARTMENT_READ, ctx.organization_id)
        return await self.dept_repo.list_by_organization(ctx.organization_id)


class DesignationService(BaseApplicationService):
    def __init__(
        self,
        des_repo: DesignationRepository,
        dept_repo: DepartmentRepository,
        auth_service: AuthorizationService | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        super().__init__(auth_service, event_bus)
        self.des_repo = des_repo
        self.dept_repo = dept_repo

    async def create_designation(
        self,
        ctx: TenantContext,
        name: str,
        code: str,
        description: str | None = None,
        level: int = 1,
        department_id: str | None = None,
    ) -> Designation:
        actor = ctx.to_actor("DesignationService.create_designation")
        self.auth.enforce(actor, HRMSAction.DESIGNATION_CREATE, ctx.organization_id)

        if department_id:
            dept = await self.dept_repo.get_by_id(ctx.organization_id, department_id)
            if not dept or dept.organization_id != ctx.organization_id:
                raise CrossTenantViolation("Department", department_id, ctx.organization_id)

        des = Designation(
            organization_id=ctx.organization_id,
            name=name,
            code=code,
            description=description,
            level=level,
            department_id=department_id,
        )
        saved = await self.des_repo.create(des)

        event = DesignationCreated(
            organization_id=ctx.organization_id,
            aggregate_id=saved.designation_id,
            actor=actor.model_dump(),
            metadata={"name": name, "code": code},
        )
        await self._publish(event, actor.actor_id)
        return saved

    async def list_designations(self, ctx: TenantContext) -> Sequence[Designation]:
        actor = ctx.to_actor("DesignationService.list_designations")
        self.auth.enforce(actor, HRMSAction.DESIGNATION_READ, ctx.organization_id)
        return await self.des_repo.list_by_organization(ctx.organization_id)


class EmployeeService(BaseApplicationService):
    def __init__(
        self,
        emp_repo: EmployeeRepository,
        dept_repo: DepartmentRepository,
        des_repo: DesignationRepository,
        auth_service: AuthorizationService | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        super().__init__(auth_service, event_bus)
        self.emp_repo = emp_repo
        self.dept_repo = dept_repo
        self.des_repo = des_repo

    async def create_employee(
        self,
        ctx: TenantContext,
        employee_code: str,
        first_name: str,
        last_name: str,
        email: str,
        department_id: str,
        designation_id: str,
        joining_date: str | date,
        preferred_name: str | None = None,
        phone: str | None = None,
        manager_id: str | None = None,
        employment_type: EmploymentType = EmploymentType.FULL_TIME,
        location: str | None = None,
        timezone: str = "Asia/Kolkata",
    ) -> Employee:
        actor = ctx.to_actor("EmployeeService.create_employee")
        self.auth.enforce(actor, HRMSAction.EMPLOYEE_CREATE, ctx.organization_id)

        existing = await self.emp_repo.get_by_code(ctx.organization_id, employee_code)
        if existing:
            raise DuplicateEmployeeCode(employee_code, ctx.organization_id)

        dept = await self.dept_repo.get_by_id(ctx.organization_id, department_id)
        if not dept or dept.organization_id != ctx.organization_id:
            raise CrossTenantViolation("Department", department_id, ctx.organization_id)

        des = await self.des_repo.get_by_id(ctx.organization_id, designation_id)
        if not des or des.organization_id != ctx.organization_id:
            raise CrossTenantViolation("Designation", designation_id, ctx.organization_id)

        if manager_id:
            mgr = await self.emp_repo.get_by_id(ctx.organization_id, manager_id)
            if not mgr or mgr.organization_id != ctx.organization_id:
                raise CrossTenantViolation("Employee (Manager)", manager_id, ctx.organization_id)

        parsed_joining_date = date.fromisoformat(joining_date) if isinstance(joining_date, str) else joining_date

        emp = Employee(
            organization_id=ctx.organization_id,
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            preferred_name=preferred_name,
            email=email,
            phone=phone,
            department_id=department_id,
            designation_id=designation_id,
            manager_id=manager_id,
            employment_type=employment_type,
            employment_status=EmploymentStatus.ACTIVE,
            joining_date=parsed_joining_date,
            location=location,
            timezone=timezone,
        )
        saved = await self.emp_repo.create(emp)

        event = EmployeeCreated(
            organization_id=ctx.organization_id,
            aggregate_id=saved.employee_id,
            actor=actor.model_dump(),
            metadata={"employee_code": employee_code, "full_name": saved.full_name},
        )
        await self._publish(event, actor.actor_id)
        return saved

    async def get_employee(self, ctx: TenantContext, employee_id: str) -> Employee:
        actor = ctx.to_actor("EmployeeService.get_employee")
        self.auth.enforce(actor, HRMSAction.EMPLOYEE_READ, ctx.organization_id)

        emp = await self.emp_repo.get_by_id(ctx.organization_id, employee_id)
        if not emp:
            raise EmployeeNotFound(employee_id)
        if emp.organization_id != ctx.organization_id:
            raise CrossTenantViolation("Employee", employee_id, ctx.organization_id)
        return emp

    async def list_employees(
        self,
        ctx: TenantContext,
        department_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Employee]:
        actor = ctx.to_actor("EmployeeService.list_employees")
        self.auth.enforce(actor, HRMSAction.EMPLOYEE_READ, ctx.organization_id)
        return await self.emp_repo.list_by_organization(ctx.organization_id, department_id, limit, offset)

    async def update_employee_status(
        self,
        ctx: TenantContext,
        employee_id: str,
        target_status: EmploymentStatus,
    ) -> Employee:
        actor = ctx.to_actor("EmployeeService.update_employee_status")
        self.auth.enforce(actor, HRMSAction.EMPLOYEE_UPDATE, ctx.organization_id)

        emp = await self.get_employee(ctx, employee_id)
        emp.transition_status(target_status)
        updated = await self.emp_repo.update(emp)

        if target_status == EmploymentStatus.TERMINATED:
            event: DomainEvent = EmployeeTerminated(
                organization_id=ctx.organization_id,
                aggregate_id=updated.employee_id,
                actor=actor.model_dump(),
                metadata={"new_status": target_status.value},
            )
        elif target_status == EmploymentStatus.RESIGNED:
            event = EmployeeResigned(
                organization_id=ctx.organization_id,
                aggregate_id=updated.employee_id,
                actor=actor.model_dump(),
                metadata={"new_status": target_status.value},
            )
        else:
            event = EmployeeUpdated(
                organization_id=ctx.organization_id,
                aggregate_id=updated.employee_id,
                actor=actor.model_dump(),
                metadata={"new_status": target_status.value},
            )
        await self._publish(event, actor.actor_id)
        return updated


class SkillService(BaseApplicationService):
    def __init__(
        self,
        skill_repo: SkillRepository,
        emp_skill_repo: EmployeeSkillRepository,
        emp_repo: EmployeeRepository,
        auth_service: AuthorizationService | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        super().__init__(auth_service, event_bus)
        self.skill_repo = skill_repo
        self.emp_skill_repo = emp_skill_repo
        self.emp_repo = emp_repo

    async def create_skill(
        self,
        ctx: TenantContext,
        name: str,
        category: SkillCategory | str = SkillCategory.TECHNICAL,
        description: str | None = None,
    ) -> Skill:
        actor = ctx.to_actor("SkillService.create_skill")
        self.auth.enforce(actor, HRMSAction.EMPLOYEE_MANAGE_SKILLS, ctx.organization_id)

        cat_enum = SkillCategory(category) if isinstance(category, str) else category
        skill = Skill(organization_id=ctx.organization_id, name=name, category=cat_enum, description=description)
        return await self.skill_repo.create(skill)

    async def add_employee_skill(
        self,
        ctx: TenantContext,
        employee_id: str,
        skill_id: str,
        proficiency: Proficiency = Proficiency.INTERMEDIATE,
        years_experience: float = 0.0,
    ) -> EmployeeSkill:
        actor = ctx.to_actor("SkillService.add_employee_skill")
        self.auth.enforce(actor, HRMSAction.EMPLOYEE_MANAGE_SKILLS, ctx.organization_id)

        emp = await self.emp_repo.get_by_id(ctx.organization_id, employee_id)
        if not emp or emp.organization_id != ctx.organization_id:
            raise CrossTenantViolation("Employee", employee_id, ctx.organization_id)

        sk = await self.skill_repo.get_by_id(ctx.organization_id, skill_id)
        if not sk or sk.organization_id != ctx.organization_id:
            raise InvalidSkill(skill_id)

        emp_skill = EmployeeSkill(
            organization_id=ctx.organization_id,
            employee_id=employee_id,
            skill_id=skill_id,
            proficiency=proficiency,
            years_experience=years_experience,
        )
        saved = await self.emp_skill_repo.create(emp_skill)

        event = EmployeeSkillAdded(
            organization_id=ctx.organization_id,
            aggregate_id=saved.employee_skill_id,
            actor=actor.model_dump(),
            metadata={"employee_id": employee_id, "skill_id": skill_id, "proficiency": proficiency.value},
        )
        await self._publish(event, actor.actor_id)
        return saved


class EmployeeDocumentService(BaseApplicationService):
    def __init__(
        self,
        doc_repo: EmployeeDocumentRepository,
        emp_repo: EmployeeRepository,
        auth_service: AuthorizationService | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        super().__init__(auth_service, event_bus)
        self.doc_repo = doc_repo
        self.emp_repo = emp_repo

    async def upload_document_metadata(
        self,
        ctx: TenantContext,
        employee_id: str,
        document_type: DocumentType,
        document_name: str,
        storage_reference: str,
        mime_type: str = "application/pdf",
        size: int = 0,
        checksum: str | None = None,
    ) -> EmployeeDocument:
        actor = ctx.to_actor("EmployeeDocumentService.upload_document_metadata")
        self.auth.enforce(actor, HRMSAction.EMPLOYEE_UPLOAD_DOCUMENT, ctx.organization_id)

        emp = await self.emp_repo.get_by_id(ctx.organization_id, employee_id)
        if not emp or emp.organization_id != ctx.organization_id:
            raise CrossTenantViolation("Employee", employee_id, ctx.organization_id)

        doc = EmployeeDocument(
            organization_id=ctx.organization_id,
            employee_id=employee_id,
            document_type=document_type,
            document_name=document_name,
            storage_reference=storage_reference,
            mime_type=mime_type,
            size=size,
            checksum=checksum,
        )
        saved = await self.doc_repo.create(doc)

        event = EmployeeDocumentUploaded(
            organization_id=ctx.organization_id,
            aggregate_id=saved.document_id,
            actor=actor.model_dump(),
            metadata={"employee_id": employee_id, "document_name": document_name},
        )
        await self._publish(event, actor.actor_id)
        return saved

    async def verify_document(self, ctx: TenantContext, document_id: str) -> EmployeeDocument:
        actor = ctx.to_actor("EmployeeDocumentService.verify_document")
        self.auth.enforce(actor, HRMSAction.EMPLOYEE_VERIFY_DOCUMENT, ctx.organization_id)

        doc = await self.doc_repo.get_by_id(ctx.organization_id, document_id)
        if not doc:
            raise DocumentNotFound(document_id)
        if doc.organization_id != ctx.organization_id:
            raise CrossTenantViolation("Document", document_id, ctx.organization_id)

        doc.verification_status = VerificationStatus.VERIFIED
        doc.verified_by = actor.actor_id
        doc.verified_at = utc_now()
        updated = await self.doc_repo.update(doc)

        event = EmployeeDocumentVerified(
            organization_id=ctx.organization_id,
            aggregate_id=updated.document_id,
            actor=actor.model_dump(),
            metadata={"verified_by": actor.actor_id},
        )
        await self._publish(event, actor.actor_id)
        return updated
