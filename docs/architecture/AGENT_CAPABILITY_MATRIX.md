# Agent Capability Matrix

## 1. Security & Principle of Least Privilege

Capabilities represent discrete operational permissions granted to agents.
Under the enterprise governance architecture:
- Capabilities are strictly declared in `CapabilityProfile`.
- Every agent has explicit **Prohibited Capabilities** ensuring zero capability creep.
- AI Agents can **never** self-grant capabilities via LLM reasoning.

---

## 2. High-Impact Prohibited Capabilities Matrix

| Prohibited Capability Token | Guaranteed Denied Agents | Enforcement Mechanism |
| :--- | :--- | :--- |
| `employee:terminate` | All 24 AI Agents (Termination is strictly human/HITL-bound) | CommandBus Authorization + PolicyEngine |
| `salary:update` / `payroll:modify` | All 24 AI Agents (Compensation modifications require HR/Finance HITL) | PolicyEngine Rule `POL-PAYROLL-001` |
| `security:modify_policy` | All 24 AI Agents (Security policies require Super Admin) | RBAC & Security Kernel |
| `employee:read_other_salary` | `EMPLOYEE_ASSISTANT_AGENT`, `CAREER_COACH_AGENT`, etc. | Tenant & Employee Boundary Isolation |
| `violation:conceal` | `COMPLIANCE_AGENT`, `AUDIT_AGENT` | Audit Trail Immutability & Event Outbox |
| `sql:arbitrary_mutation` | `HR_ANALYTICS_AGENT`, `DOCUMENT_INTELLIGENCE_AGENT` | SQL AST Guardrails & Read-Only Pool |
