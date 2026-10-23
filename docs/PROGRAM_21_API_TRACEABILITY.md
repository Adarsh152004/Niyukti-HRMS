# Program 21: UI-to-API-to-Database Traceability Matrix

## 1. End-to-End Traceability Mapping

| Screen / Feature | Frontend Route | HTTP Endpoint & Method | Backend Application Service | Domain Aggregate / Target | Repository / Persistence | Event Staged in Outbox |
|---|---|---|---|---|---|---|
| **AI HR Assistant** | `/assistant` | `POST /api/v1/ai/command` | `AICommandService` | `AIAgentContext` | `MemoryRepository` + `VectorStore` | `AITaskCompletedEvent` |
| **Approvals Queue** | `/approvals` | `GET /api/v1/approvals/pending` | `ApprovalInboxService` | `ApprovalRequest` | `ApprovalRepository` | `ApprovalViewedEvent` |
| **Approve / Reject Action** | `/approvals` | `POST /api/v1/approvals/{id}/decide` | `ApprovalInboxService` | `ApprovalRequest` $\to$ `CommandBus` | `PostgresUnitOfWork` | `ApprovalDecidedEvent` |
| **Employee Directory** | `/employees` | `GET /api/v1/employees` | `EmployeeService` | `EmployeeAggregate` | `PostgresEmployeeRepository` | None (Read Query) |
| **Employee 360 Portal** | `/employees/:id`| `GET /api/v1/employee-360/:id` | `Employee360Service` | `Employee360View` | Multi-Domain Aggregation | None (Read Query) |
| **Executive Dashboard**| `/dashboard` | `GET /api/v1/executive/cockpit` | `ExecutiveControlService` | `ExecutiveMetrics` | `KPIService` / `PostgresViews` | None (Read Query) |
| **Attendance Timesheet**| `/attendance` | `GET /api/v1/attendance` | `AttendanceService` | `AttendanceRecord` | `PostgresAttendanceRepository`| None (Read Query) |
| **Leave Management** | `/leave` | `GET /api/v1/leave/requests` | `LeaveService` | `LeaveRequest` | `PostgresLeaveRepository` | None (Read Query) |
| **Recruitment & ATS** | `/recruitment` | `GET /api/v1/recruitment/jobs` | `RecruitmentService` | `JobRequisition`, `Candidate`| `PostgresRecruitmentRepository`| None (Read Query) |
| **Payroll Processing**| `/payroll` | `GET /api/v1/payroll/runs` | `PayrollService` | `PayrollRun`, `Payslip` | `PostgresPayrollRepository` | None (Read Query) |
| **Governance & KillSwitch**| `/governance` | `GET /api/v1/governance/kill-switch/status`| `GovernanceService` | `KillSwitchState` | `RedisClient` + `AuditLedger` | `KillSwitchToggledEvent`|
| **Document Brain** | `/documents` | `GET /api/v1/documents` | `DocumentIntelligenceService`| `KnowledgeDocument` | `DocumentRepository` + Storage | None (Read Query) |
| **Predictive ML Center**| `/ml` | `GET /api/v1/analytics/ml/metrics` | `MLContinuousEvalRunner` | `MLModelRegistry` | `ModelRepository` | None (Read Query) |
