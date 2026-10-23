# Program 21: Specialized Agent Fleet & Supervisor-Worker Orchestration

## 1. Supervisor-Worker Hierarchy & Delegation Rules
1. **Bounded Recursion Depth**: Maximum delegation depth $\le 3$.
2. **Capability Intersection**: A delegated worker agent inherits only the *intersection* of its own capabilities and the supervisor's capabilities.
3. **Tenant Strictness**: Delegation context remains strictly bound to the origin `organization_id`.
4. **Execution Budgets**: Max tools per task (5–15 depending on role) and max duration (120s timeout).

```text
                        ┌────────────────────────┐
                        │   EXECUTIVE HR AGENT   │ (Supervisor, Depth 0)
                        └───────────┬────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌───────────────────────┐ ┌───────────────────┐ ┌───────────────────────┐
│ WORKFORCE SUPERVISOR  │ │ RECRUITMENT SUPER │ │ COMPLIANCE SUPERVISOR │ (Depth 1)
└───────────┬───────────┘ └─────────┬─────────┘ └───────────┬───────────┘
            │                       │                       │
      ┌─────┴─────┐           ┌─────┴─────┐           ┌─────┴─────┐
      ▼           ▼           ▼           ▼           ▼           ▼
   Attrition  Performance  Screening   Ranking    Audit Log   Data Privacy  (Workers, Depth 2)
```
