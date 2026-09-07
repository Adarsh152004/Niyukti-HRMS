# Program 20: 20 Automated End-to-End Business Scenarios

## Verification Scenarios Summary

| # | Business Scenario Name | Participating Agents / Services | Expected Security & Governance Outcome |
|---|---|---|---|
| 1 | CEO Workforce Overview | CEO Agent, KPI Engine, DB Repositories | Verified tenant scope, calculated metrics (128 headcount, 94.6% attendance) |
| 2 | Employee Leave Balance Query | Employee Assistant, Leave Repository | Scoped strictly to authenticated employee profile |
| 3 | Manager Team Attendance Query | HR Manager, Attendance Service | Scoped to manager's department; anomalies flagged |
| 4 | HR Incomplete Onboarding Check| Onboarding Agent, Employee Repository | Returns list of pending employee onboarding tasks |
| 5 | Attrition Risk ML Prediction | Predictive ML, Retention Intervention Agent | Returns calibrated flight risk scores with decision lineage |
| 6 | Employee Termination Proposal | Offboarding Agent, Governed MCP Server | Risk CRITICAL $\to$ Halted; `ApprovalRequest` created (NO immediate DB write) |
| 7 | Authorized Human Approval | Super Admin / CEO, CommandBus, Outbox | Dispatches command, commits PostgreSQL UoW, emits `EmployeeTerminated` |
| 8 | Unauthorized Termination Attempt | Standard Employee Actor | HTTP 403 Forbidden; audit alert logged |
| 9 | Cross-Tenant Data Access Attempt | Tenant A accessing Tenant B resource | HTTP 403 Forbidden; zero data leakage |
| 10 | Prompt Injection Neutralization | Prompt Firewall, AI Gateway | Neutralizes jailbreaks; treats malicious injection as literal data |
| 11 | Primary LLM Outage Failover | LLMRouter | Automatic fallback from Primary $\to$ Secondary $\to$ Safe Mock |
| 12 | Total LLM Cloud Disconnect | LLMRouter | Graceful fallback to deterministic offline mock |
| 13 | Redis Service Interruption | RedisClient | Controlled fallback to in-memory local lock/cache in dev |
| 14 | Database Transaction Rollback | UnitOfWork | Atomically rolls back failed mutations; Outbox remains empty |
| 15 | Duplicate Command Idempotency | CommandBus, IdempotencyManager | Returns cached result without executing duplicate mutations |
| 16 | Agent SLA / Sandbox Breach | Sandbox Monitor | Terminates runaway tasks exceeding execution limits |
| 17 | Emergency AI Kill-Switch | Governance KillSwitch API | Global pause stops all AI agent tasks; audit recorded |
| 18 | Out-of-Distribution ML Input | Predictive ML Engine | Emits `Decision.ABSTAIN` with uncertainty flag |
| 19 | Unauthorized RAG Search | Knowledge Engine | Pre-retrieval authorization blocks unauthorized confidential policy access |
| 20 | Multi-Level Agent Delegation | Supervisor $\to$ Worker DAG | Strict capability intersection; max depth $\le 3$ enforced |
