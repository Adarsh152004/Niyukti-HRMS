# Program 18: Enterprise Security, RBAC/ABAC & Multi-Tenancy Governance

## 1. Authentication & Session Architecture

- **Token Pair**: Dual-token architecture:
  - **Access Token**: Short-lived (60 min) signed JWT holding subject (`actor_id`), tenant (`organization_id`), `roles`, `permissions`, and `capabilities`.
  - **Refresh Token**: Long-lived (7 days) rotating cryptographic token with family tracking for instant reuse detection.
- **API Keys**: Inter-service and agent integrations authenticate via SHA-256 salted API keys with explicit scope bindings (`ak_live_*`).

---

## 2. Multi-Tenancy Boundary Isolation

- **Tenant Identifier**: `organization_id` is propagated via JWT claims and validated against `X-Tenant-ID` header.
- **Zero Cross-Tenant Leakage**:
  - **Database Queries**: Explicit `where(Model.organization_id == tenant_id)` on all repository read/write operations.
  - **Redis Cache**: Keys are namespaced as `hrms:{tenant_id}:{namespace}:{key}`.
  - **Object Storage**: Paths isolated as `storage_data/{tenant_id}/{object_key}`.
  - **Vector Database**: Namespace partitions prevent semantic vector search leaks across tenants.
  - **Cross-Tenant Attack**: Attempting to query another tenant's records immediately triggers HTTP 403 Forbidden and emits a security audit event.

---

## 3. RBAC & ABAC Access Control Matrix

| Role | Permitted Actions | Prohibited Actions |
|---|---|---|
| `SUPER_ADMIN` | Global tenant management, system diagnostics, configuration | Cross-tenant data inspection without explicit tenant switch |
| `CEO / EXECUTIVE` | Organization-wide KPI summaries, AI queries, executive approvals | Raw payroll ledger mutation, single-employee clock-in edits |
| `HR_ADMIN` | Full workforce management, onboarding, policy publishing, recruitment | System-level kernel configuration bypass |
| `MANAGER` | Direct report approvals (Leave, Performance, Overtime), team KPIs | Modification of other department's employees, global payroll release |
| `PAYROLL_ADMIN`| Batch payroll calculation, preview, tax withholding, payslip issuance | Unsupervised bulk compensation adjustment without HITL approval |
| `RECRUITER` | Job postings, candidate sourcing, interview coordination | Final employment offer letter release without HR approval |
| `EMPLOYEE` | View personal profile, submit leave, clock attendance, view own payslips | Access to coworker salaries, performance reviews, or management KPIs |
| `AUDITOR` | Read-only access to tamper-evident audit ledger and compliance reports | Any database mutation or agent task execution |
| `AI_OPERATOR` | Agent fleet monitoring, kill-switch pause/resume, model calibration | Authoritative approval of financial or termination transactions |

---

## 4. Adversarial AI Defense Stack

1. **Data Minimization Firewall**: Strips unneeded PII fields (SSN, home address, bank accounts) prior to constructing prompts for external LLM models.
2. **Prompt Injection Neutralization**: Document and user inputs are passed through injection filters that strip malicious jailbreak directives (`"Ignore all previous rules..."`, `"System Prompt Override"`). Documents are treated as untrusted DATA, never as executable INSTRUCTIONS.
3. **Autonomy Guardrail**: Autonomous agents cannot grant themselves capabilities, modify policies, approve their own requests, or alter the cryptographic audit chain.
