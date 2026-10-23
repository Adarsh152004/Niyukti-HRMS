# Database & Persistence Architecture — AI-Powered Intelligent HRMS

## 1. Overview
The database layer provides a production-grade, asynchronous PostgreSQL persistence architecture built with SQLAlchemy 2.x and asyncpg. It maintains strict architectural separation from the domain layer, ensuring that domain entities remain pure Pydantic models completely free of ORM frameworks.

```
Domain (Pydantic Models)
    ↑
  Mappers (Bi-directional Mapping)
    ↓
Application Services (Business Logic)
    ↓
Repository Ports (Abstract Interfaces)
    ↓
PostgreSQL Infrastructure (AsyncSession, SQLAlchemy 2.x, RLS)
```

---

## 2. Key Architectural Invariants

### 1. Domain Decoupling
- Domain models (`backend/hrms/domain/`) have zero imports or inheritance from SQLAlchemy.
- Persistence models (`backend/hrms/infrastructure/database/models/`) mirror database tables.
- Bi-directional mappers (`backend/hrms/infrastructure/database/mappers/mappers.py`) translate between domain models and persistence models deterministically.

### 2. Multi-Tenant Scoping & Row-Level Security (RLS)
- Every tenant-owned persistence table carries `organization_id`.
- Composite unique constraints are strictly tenant-scoped (`UNIQUE(organization_id, code)`, `UNIQUE(organization_id, employee_code)`).
- Session helper `set_tenant_session_context(session, org_id)` sets `SET LOCAL app.current_organization_id = :org_id` in PostgreSQL for defense-in-depth RLS enforcement.

### 3. Unit of Work & Transactional Outbox
- Multi-step operations execute inside `UnitOfWork` async context managers (`async with unit_of_work:`).
- `stage_outbox_event()` writes business entity state changes and `OutboxEventModel` records atomically into the `outbox_events` table within a single database transaction before `commit()`.

---

## 3. Database Schema Overview

| Table | Primary Key | Foreign Keys | Tenant Scoped Uniqueness |
| :--- | :--- | :--- | :--- |
| `organizations` | `id` | None | `slug` (Global) |
| `departments` | `id` | `organization_id` → `organizations.id` | `(organization_id, code)` |
| `designations` | `id` | `organization_id`, `department_id` | `(organization_id, code)` |
| `roles` | `id` | `organization_id` | `(organization_id, code)` |
| `employees` | `id` | `organization_id`, `department_id`, `designation_id`, `manager_id` → `employees.id` | `(organization_id, employee_code)`, `(organization_id, email)` |
| `skills` | `id` | `organization_id` | `(organization_id, name)` |
| `employee_skills` | `id` | `organization_id`, `employee_id`, `skill_id` | `(organization_id, employee_id, skill_id)` |
| `employee_documents` | `id` | `organization_id`, `employee_id` | `id` |
| `outbox_events` | `id` | None | `event_id` |

---

## 4. Alembic Migrations
Migrations are managed via Alembic using async SQLAlchemy drivers:
```bash
# Apply migrations to head
alembic upgrade head

# Rollback single revision
alembic downgrade -1
```

Initial migration revision: `001_initial_hrms_schema`.

---

## 5. Security & Data Governance
- Sensitive credentials and DB passwords are never committed to version control (`.env.example` provides non-production defaults).
- Employee salary and compensation details are excluded from basic employee persistence tables to adhere to PII minimization guidelines.
- AI agents NEVER execute raw SQL directly; all database access flows strictly through authorized Application Services and Repository Interfaces.
