# AI-Powered Intelligent HRMS — Human-in-the-Loop (HITL) Governance & Approval Architecture

## 1. Core Principles & Non-Negotiable Invariants

$$\mathbf{LLM \neq AUTHORITY}$$

1. **Autonomous Mutation Prohibition**: No AI agent or LLM prompt can directly commit state changes affecting compensation, employment termination, or bulk database updates.
2. **Approval Request Gating**: Any tool proposal categorized as `HIGH` or `CRITICAL` risk automatically halts task execution, creates an `ApprovalRequest` entity, and yields to the Human Approver.
3. **Cryptographic Linkage**: Once approved by an authorized human actor, the approval hash is injected into the Command payload and committed to the append-only SHA-256 audit ledger.
4. **Self-Approval Ban**: An AI agent cannot approve its own requests under any circumstances.

---

## 2. Approval Request Lifecycle States

```text
                  [Tool Proposal with Risk >= HIGH]
                                 │
                                 ▼
                          [State: PENDING]
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   [State: APPROVED]     [State: REJECTED]       [State: EXPIRED]
         │                       │                       │
         ▼                       ▼                       ▼
[CommandBus Dispatches]   [Task Cancelled]       [Task Terminated]
[PostgreSQL Committed]   [Audit Logged]         [Audit Logged]
[Audit Ledger Staged]
```

---

## 3. Human Approval UI Schema

The `/approvals` UI provides human decision-makers with comprehensive context:
- **`approval_id`**: Unique cryptographic identifier.
- **`requesting_agent`**: Autonomous agent name, system role, and session ID.
- **`risk_level`**: `HIGH` or `CRITICAL` with visual warning badge.
- **`proposed_mutation`**: Exact field-level diff (e.g. `base_salary: $120,000 -> $145,000`).
- **`policy_and_evidence`**: Verifiable citations from retrieved company policies and ML confidence metrics.
- **`affected_records`**: Target employee IDs, departments, and financial impacts.
