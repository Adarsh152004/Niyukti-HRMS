# AI-Powered Intelligent HRMS — Governed MCP Tool Catalog

## 1. Governance Architecture
All tool executions are authenticated against the caller's authorized capability scope. High-risk actions automatically halt autonomous execution and dispatch a `HITLApprovalRequest` to the Human-in-the-Loop approval queue.

---

## 2. Canonical Tool Registry Matrix

| Tool Name | Domain / Resource | Target Action | Risk Level | Requires HITL | Required Capability | Idempotency | Timeout |
|---|---|---|---|---|---|---|---|
| `employee.get` | Employees | Read single employee profile | LOW | `false` | `EMPLOYEE_READ` | N/A | 5s |
| `employee.list` | Employees | Query employee directory | LOW | `false` | `EMPLOYEE_READ` | N/A | 10s |
| `employee.update` | Employees | Update contact/profile details | MEDIUM | `false` | `EMPLOYEE_WRITE` | Required | 10s |
| `employee.terminate` | Employees | Initiate employee termination | CRITICAL | `true` | `EMPLOYEE_ADMIN` | Required | 15s |
| `attendance.summary` | Attendance | Aggregate shift metrics | LOW | `false` | `ATTENDANCE_READ` | N/A | 5s |
| `attendance.correct` | Attendance | Adjust clock-in/out timestamp | MEDIUM | `true` | `ATTENDANCE_WRITE`| Required | 10s |
| `leave.balance` | Leave | Query remaining leave credits | LOW | `false` | `LEAVE_READ` | N/A | 5s |
| `leave.request` | Leave | Submit leave application | MEDIUM | `false` | `LEAVE_REQUEST` | Required | 10s |
| `leave.approve` | Leave | Approve submitted leave request| MEDIUM | `true` | `LEAVE_APPROVE` | Required | 10s |
| `payroll.preview` | Payroll | Preview calculated draft runs | LOW | `false` | `PAYROLL_READ` | N/A | 15s |
| `payroll.update_salary` | Payroll | Adjust employee compensation | HIGH | `true` | `PAYROLL_WRITE` | Required | 10s |
| `payroll.finalize` | Payroll | Commit and publish monthly run | CRITICAL | `true` | `PAYROLL_APPROVE`| Required | 30s |
| `candidate.screen` | Recruitment | Parse and score resume text | LOW | `false` | `CANDIDATE_READ` | N/A | 15s |
| `candidate.move_stage` | Recruitment | Advance candidate in pipeline | MEDIUM | `false` | `CANDIDATE_WRITE`| Required | 10s |
| `knowledge.search` | Knowledge | Semantic RAG policy search | LOW | `false` | `POLICY_READ` | N/A | 10s |
| `notification.send` | Notifications | Multi-channel message dispatch| LOW | `false` | `NOTIFICATION_SEND`| Required| 10s |
