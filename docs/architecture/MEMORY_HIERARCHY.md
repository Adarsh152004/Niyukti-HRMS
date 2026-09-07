# Hierarchical Memory Architecture

## 1. Memory Tiers Overview

To prevent cognitive clutter and cross-tenant or cross-squad data leaks, the HRMS partitions agent memory into 4 strictly isolated tiers:

```
┌─────────────────────────────────────────────────────────┐
│                   ORGANIZATION MEMORY                   │
│     Company-wide authorized policies, SOPs, holidays    │
├─────────────────────────────────────────────────────────┤
│                       TEAM MEMORY                       │
│    Squad-shared collaboration (e.g. Recruitment squad)  │
├─────────────────────────────────────────────────────────┤
│                      AGENT MEMORY                       │
│      Private episodic scratchpad for single agent       │
├─────────────────────────────────────────────────────────┤
│                     EMPLOYEE MEMORY                     │
│    Employee-specific private conversational context     │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Partition Authorization Rules

| Memory Tier | Required Owner ID | Read Authorization | Write Authorization |
| :--- | :--- | :--- | :--- |
| **`AGENT`** | `agent_id` | Only the specific `agent_id` | That specific agent only |
| **`TEAM`** | `team_id` | Members of the agent squad | Squad agents & supervisor |
| **`ORGANIZATION`** | `organization_id` | All authorized actors in tenant | System & HR Admins |
| **`EMPLOYEE`** | `employee_id` | The employee & authorized HR | The employee & assigned assistant |

---

## 3. Structured Write Policy

- **No Raw Chain-of-Thought (CoT)**: Internal reasoning artifacts are scrubbed.
- **Validated Facts Only**: Persists only tool results, observations, task results, and user preferences.
- **Expiration Support**: Time-to-live (`expires_at`) cleans up transient task context automatically.
