# Program 22: UI-to-API-to-Database Traceability Matrix

## 1. Traceability Mapping

| Feature / UI Route | HTTP Endpoint & Method | Service Layer | Domain Aggregate | Repository / Storage | Transactional Outbox Event |
|---|---|---|---|---|---|
| **AI Assistant** (`/assistant`) | `POST /api/v1/ai/command` | `AICommandService` | `AIAgentContext` | `MemoryRepository` + `VectorStore` | `AITaskCompletedEvent` |
| **Approvals Queue** (`/approvals`) | `GET /api/v1/approvals/pending` | `ApprovalInboxService` | `ApprovalRequest` | `ApprovalRepository` | `ApprovalViewedEvent` |
| **Sign-Off Action** (`/approvals`) | `POST /api/v1/approvals/{id}/decide`| `ApprovalInboxService` | `ApprovalRequest` $\to$ `CommandBus` | `PostgresUnitOfWork` | `ApprovalDecidedEvent` |
| **Employee Directory** (`/employees`) | `GET /api/v1/employees` | `EmployeeService` | `EmployeeAggregate` | `PostgresEmployeeRepository` | None (Read Query) |
| **Employee 360** (`/employees/:id`)| `GET /api/v1/employee-360/:id` | `Employee360Service` | `Employee360View` | Multi-Domain Repository | None (Read Query) |
| **Executive Cockpit** (`/dashboard`)| `GET /api/v1/executive/cockpit` | `ExecutiveControlService`| `ExecutiveMetrics` | `KPIService` / Postgres Views | None (Read Query) |
| **Attendance Sheet** (`/attendance`)| `GET /api/v1/attendance` | `AttendanceService` | `AttendanceRecord` | `PostgresAttendanceRepository`| None (Read Query) |
| **Leave Management** (`/leave`) | `GET /api/v1/leave/requests` | `LeaveService` | `LeaveRequest` | `PostgresLeaveRepository` | None (Read Query) |
| **Recruitment ATS** (`/recruitment`)| `GET /api/v1/recruitment/jobs` | `RecruitmentService` | `JobRequisition`, `Candidate`| `PostgresRecruitmentRepository`| None (Read Query) |
| **Payroll Processing** (`/payroll`) | `GET /api/v1/payroll/runs` | `PayrollService` | `PayrollRun`, `Payslip` | `PostgresPayrollRepository` | None (Read Query) |
| **Governance & Kill-Switch** (`/governance`)| `GET /api/v1/governance/kill-switch/status`| `GovernanceService` | `KillSwitchState` | `RedisClient` + `AuditLedger` | `KillSwitchToggledEvent` |
