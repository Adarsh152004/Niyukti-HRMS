# Agent Tool Access Matrix

## 1. Tool Governance Principles

Every tool execution by an AI Agent is evaluated against its declarative `ToolPolicy`:
- **`ALLOW`**: Direct execution permitted (low risk, read-only, or pre-approved).
- **`REQUIRES_APPROVAL`**: Generates a pending Approval Ticket requiring human manager confirmation before CommandBus execution.
- **`DENY`**: Instant server-side rejection with `ProhibitedToolExecutionError`. Undeclared tools default to `DENY`.

---

## 2. Representative Tool Policy Matrix

| Agent Role | Tool ID | Access Level | Rationale |
| :--- | :--- | :--- | :--- |
| `EXECUTIVE_HR_AGENT` | `analytics.query` | `ALLOW` | Authorized executive read |
| `EXECUTIVE_HR_AGENT` | `employee.terminate` | `DENY` | High-impact action blocked |
| `RECRUITMENT_AGENT` | `candidate.reject` | `REQUIRES_APPROVAL` | High-impact candidate outcome requires human approval |
| `RECRUITMENT_AGENT` | `interview.schedule` | `ALLOW` | Automated low-risk coordination |
| `RESUME_SCREENING_AGENT` | `resume.parse` | `ALLOW` | Untrusted parsing under DataFirewall |
| `RESUME_SCREENING_AGENT` | `candidate.hire` | `DENY` | Screening agent cannot make hiring decisions |
| `EMPLOYEE_ASSISTANT_AGENT`| `leave.get_own_balance` | `ALLOW` | Self-service balance lookup |
| `EMPLOYEE_ASSISTANT_AGENT`| `employee.view_other_salary` | `DENY` | Privacy boundary protection |
| `PAYROLL_ASSISTANT_AGENT` | `payroll.get_payslip` | `ALLOW` | Read-only payslip explanation |
| `PAYROLL_ASSISTANT_AGENT` | `payroll.update_salary` | `DENY` | Payroll calculation remains deterministic |
| `HR_ANALYTICS_AGENT` | `database.raw_mutate_sql` | `DENY` | Arbitrary database mutations prohibited |
| `COMPLIANCE_AGENT` | `audit.delete_logs` | `DENY` | Audit logs are strictly append-only |
