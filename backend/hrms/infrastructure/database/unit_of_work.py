"""
Unit of Work — Transactional boundary & Outbox event staging.

Guarantees atomic execution:
- All domain mutations and outbox events commit together in a single DB transaction.
- Automatic rollback if any step fails.
"""

from __future__ import annotations

import uuid
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import AsyncSessionLocal
from backend.hrms.domain.events import DomainEvent
from backend.hrms.infrastructure.database.models.outbox import OutboxEventModel
from backend.hrms.infrastructure.database.repositories.repositories import (
    PostgresDepartmentRepository,
    PostgresDesignationRepository,
    PostgresEmployeeDocumentRepository,
    PostgresEmployeeRepository,
    PostgresEmployeeSkillRepository,
    PostgresOrganizationRepository,
    PostgresRoleRepository,
    PostgresSkillRepository,
)


class UnitOfWork:
    """
    Async Unit of Work managing database transactions and repository access.
    """

    def __init__(self, session: AsyncSession | None = None) -> None:
        self._external_session = session is not None
        self._session = session

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            self._session = AsyncSessionLocal()
        return self._session

    @property
    def organizations(self) -> PostgresOrganizationRepository:
        return PostgresOrganizationRepository(self.session)

    @property
    def departments(self) -> PostgresDepartmentRepository:
        return PostgresDepartmentRepository(self.session)

    @property
    def designations(self) -> PostgresDesignationRepository:
        return PostgresDesignationRepository(self.session)

    @property
    def roles(self) -> PostgresRoleRepository:
        return PostgresRoleRepository(self.session)

    @property
    def employees(self) -> PostgresEmployeeRepository:
        return PostgresEmployeeRepository(self.session)

    @property
    def skills(self) -> PostgresSkillRepository:
        return PostgresSkillRepository(self.session)

    @property
    def employee_skills(self) -> PostgresEmployeeSkillRepository:
        return PostgresEmployeeSkillRepository(self.session)

    @property
    def documents(self) -> PostgresEmployeeDocumentRepository:
        return PostgresEmployeeDocumentRepository(self.session)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        if not self._external_session and self._session is not None:
            await self._session.close()

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._session is not None:
            await self._session.rollback()

    async def stage_outbox_event(self, event: DomainEvent) -> OutboxEventModel:
        """
        Stage a domain event into outbox_events table within the active transaction.
        """
        outbox_entry = OutboxEventModel(
            id=str(uuid.uuid4()),
            organization_id=event.organization_id,
            event_id=event.event_id,
            event_type=event.event_type,
            aggregate_id=event.aggregate_id,
            payload=event.model_dump(),
            occurred_at=event.occurred_at,
            attempt_count=0,
            status="PENDING",
        )
        if self._session is not None:
            self._session.add(outbox_entry)
            await self._session.flush()
        return outbox_entry
