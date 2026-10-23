# Agent Authority & Autonomy Matrix

## 1. Non-Negotiable Invariant: $\text{AI Agent} \neq \text{Authority}$

AI agents operate across six explicit autonomy modes:
1. **`ADVISORY`**: Pure recommendation; humans execute all mutations (e.g. `CAREER_COACH_AGENT`).
2. **`ASSISTED`**: Agent drafts actions; one-click human confirmation executes (e.g. `EMPLOYEE_ASSISTANT_AGENT`, `PERFORMANCE_AGENT`).
3. **`SUPERVISED`**: Low-risk automated actions with continuous supervisor oversight (e.g. `EXECUTIVE_HR_AGENT`, `HR_MANAGER_AGENT`, `PAYROLL_ASSISTANT_AGENT`, `ATTRITION_AGENT`, `COMPLIANCE_AGENT`).
4. **`AUTONOMOUS_LOW_RISK`**: Reversible, low-risk, read-intensive operations execute automatically (e.g. `RESUME_SCREENING_AGENT`, `ATTENDANCE_AGENT`, `LEAVE_MANAGEMENT_AGENT`, `HR_ANALYTICS_AGENT`, `NOTIFICATION_AGENT`).
5. **`AUTONOMOUS_WITH_APPROVAL`**: Autonomous discovery/ranking; high-impact decisions branch to HITL (e.g. `CANDIDATE_RANKING_AGENT`).
6. **`DISABLED`**: Quarantined or deactivated by administration.

---

## 2. Command Execution Boundary

Every state mutation follows the invariant execution pipeline:
```
Agent → AgentCommandGateway → CommandBus → Authorization → PolicyEngine → RiskEngine → HITL → ActionExecutor
```
No agent can bypass any layer in this pipeline.
