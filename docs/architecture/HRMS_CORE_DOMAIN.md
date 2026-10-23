# HRMS Core Domain & Multi-Tenant Architecture

> Technical reference documentation for the foundational HRMS domain, multi-tenant boundaries, repository port abstractions, and security model.

---

## 1. Multi-Tenant Architecture

The system is designed as a SaaS platform where every customer organization represents an isolated **Tenant**.

### Core Invariants
1. **Tenant ID Boundary**: Every tenant-owned domain entity carries `organization_id`.
2. **Context Resolution**: Every request or service call must resolve `TenantContext` containing `organization_id` and acting `Actor`.
3. **Cross-Tenant Validation**: Application services strictly validate that references (e.g. `department_id`, `manager_id`, `skill_id`) belong to the SAME `organization_id`. Any cross-tenant reference raises `CrossTenantViolation`.

```
                  Tenant Context (org_id: "org-acme")
                                │
   ┌────────────────────────────┼────────────────────────────┐
   ▼                            ▼                            ▼
Department                  Employee                    Designation
(org_id: "org-acme")       (org_id: "org-acme")        (org_id: "org-acme")
```

---

## 2. Organization Hierarchy

```
Organization (Tenant)
├── Department (hierarchical via parent_department_id)
└── Designation (hierarchy level 1..N)
```

- **Organization**: `id`, `legal_name`, `display_name`, `slug`, `country`, `currency`, `status` (`ACTIVE`, `SUSPENDED`, `TRIAL`, `ARCHIVED`).
- **Department**: `id`, `organization_id`, `name`, `code`, `parent_department_id`, `manager_employee_id`, `status`.
- **Designation**: `id`, `organization_id`, `name`, `code`, `level`, `department_id`, `status`.
- **Role**: Custom tenant-specific roles containing `permissions` set.

---

## 3. Employee Domain & State Transitions

### Lifecycle States
```
         ┌───────────────┐
         │    ACTIVE     │◄──────────────┐
         └───────┬───────┘               │
                 │                       │
     ┌───────────┼───────────┐           │
     ▼           ▼           ▼           │
 ON_LEAVE    SUSPENDED   RESIGNED        │
     │           │           │           │
     └───────────┼───────────┴───────────┘
                 │
                 ▼
        TERMINATED / RETIRED (Terminal)
```

- **State Transition Enforcement**: State changes pass through `validate_status_transition`. Illegal transitions (e.g. `TERMINATED` → `ACTIVE`) raise `InvalidEmployeeState`.

---

## 4. PII Classification & Data Minimization

| Level | Examples | Encrypted at Rest | Masked in Logs | AI Agent Access |
|---|---|---|---|---|
| `PUBLIC` | Job title, department name | No | No | Yes |
| `INTERNAL` | First/last name, work email, code | No | No | Yes |
| `CONFIDENTIAL` | Phone, personal address, location | No | Yes | Explicit Grant |
| `SENSITIVE` | Date of birth, performance rating | Yes | Yes | Explicit Grant |
| `HIGHLY_SENSITIVE` | Gross salary, SSN/National ID, Bank account | Yes | Yes | Explicit Grant |

---

## 5. Persistence & Database Layer (Node 3)

The persistence layer (`backend/database/` and `backend/hrms/infrastructure/database/`) provides production-oriented PostgreSQL storage via SQLAlchemy 2.x async engine, Alembic migrations, Unit of Work, Transactional Outbox, and RLS session scoping while maintaining 100% domain model independence.

See [DATABASE_ARCHITECTURE.md](file:///e:/Major%20Project/HRMS/docs/architecture/DATABASE_ARCHITECTURE.md) for full database design details.

---

## 6. Repository Architecture (Ports)

Domain models do not depend on PostgreSQL, SQLAlchemy, or FastAPI.
Persistence operations are defined as abstract ports in `backend/hrms/ports/repositories.py`:

- `OrganizationRepository`
- `DepartmentRepository`
- `DesignationRepository`
- `RoleRepository`
- `EmployeeRepository`
- `SkillRepository`
- `EmployeeSkillRepository`
- `EmployeeDocumentRepository`

In Node 2, thread-safe in-memory implementations (`backend/hrms/infrastructure/memory_repositories.py`) satisfy these ports.

---

## 6. Application Services & Authorization

Application services orchestrate business operations and enforce security boundaries:

```
FastAPI Router
    ↓
TenantContext Resolution (from headers/tokens)
    ↓
ApplicationService (e.g. EmployeeService)
    ↓
AuthorizationService.enforce(actor, action, tenant_id)
    ↓
Cross-Tenant Reference Validation
    ↓
Domain Mutation & Event Dispatch (EventBus)
    ↓
Repository Port
```

---

## 7. Domain Events & Audit Strategy

Mutations emit typed, tenant-aware domain events:

- `OrganizationCreated`
- `DepartmentCreated`
- `EmployeeCreated`, `EmployeeUpdated`, `EmployeeJoined`, `EmployeeTransferred`, `EmployeeTerminated`
- `EmployeeSkillAdded`, `EmployeeSkillUpdated`
- `EmployeeDocumentUploaded`, `EmployeeDocumentVerified`

Every event captures `event_id`, `organization_id`, `aggregate_id`, `event_type`, `occurred_at`, `actor`, and `metadata`.

---

## 8. Future PostgreSQL & Persistence Roadmap

When PostgreSQL is introduced in subsequent nodes:
1. SQLAlchemy 2.0 async models will map 1-to-1 to these domain entities.
2. Alembic migrations will create tenant-indexed schemas.
3. Row-level security (RLS) policies using `organization_id` will enforce DB-level tenant boundaries as defense-in-depth.
