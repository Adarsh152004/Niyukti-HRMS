# Command Execution Architecture — AI-Powered Intelligent HRMS

## 1. Overview & Universal Execution Pipeline
The platform implements a universal, enterprise-grade command & action execution engine (`CommandBus`). EVERY meaningful operation—whether initiated by a Human CEO, an AI Agent, a System background process, or an External Integration—executes through the single unified pipeline:

```
                    ┌──────────────┐
                    │ CEO / HUMAN  │
                    │   AI AGENT   │
                    │   SYSTEM     │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ WEB/CLI/API  │
                    │   AGENT      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ COMMAND BUS  │
                    └──────┬───────┘
                           │
                 ┌─────────▼─────────┐
                 │   POLICY ENGINE   │
                 └─────────┬─────────┘
                           │
                 ┌─────────▼─────────┐
                 │  AUTHORIZATION    │
                 └─────────┬─────────┘
                           │
                 ┌─────────▼─────────┐
                 │    RISK ENGINE    │
                 └─────────┬─────────┘
                           │
                  ┌────────▼────────┐
                  │   HITL GATE?    │
                  └───────┬─────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ ACTION EXECUTOR│
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ DOMAIN SERVICE│
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   UNIT OF     │
                  │    WORK       │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  PostgreSQL   │
                  └───────┬───────┘
                          │
                    ┌─────▼─────┐
                    │   OUTBOX  │
                    └───────────┘
```

---

## 2. Command Lifecycle States
1. `RECEIVED`: Initial submission.
2. `VALIDATING`: Validating payload structure and checking idempotency deduplication key.
3. `AUTHORIZED`: Checking permission grants via `AuthorizationService`.
4. `POLICY_CHECKED`: Evaluating dynamic conditions via `PolicyEngine` (`ALLOW`, `DENY`, `REQUIRE_APPROVAL`).
5. `WAITING_APPROVAL`: Created `ApprovalRequest` when HITL is required (e.g. HIGH/CRITICAL risk or policy trigger).
6. `APPROVED`: Human approver approved request (verifying SHA-256 payload hash integrity).
7. `EXECUTING`: Runtime `ActionExecutor` invoking `CommandHandler`.
8. `SUCCEEDED` / `FAILED` / `DENIED` / `CANCELLED` / `EXPIRED`: Terminal execution states.

---

## 3. Policy & Risk Engines

### Policy Engine (`policy_engine.py`)
Separates business conditions from permission authorization:
- **Authorization**: "Does this actor possess permission `EMPLOYEE_CREATE`?"
- **Policy**: "Under what conditions is this action allowed?" (e.g., blocking AI Agents from altering security roles or modifying CEO compensation).

### Risk Engine (`risk_engine.py`)
Classifies command risk into tiers:
- `LOW`: Read and informational operations.
- `MEDIUM`: Standard creation/update mutations.
- `HIGH`: Personnel status terminations, financial salary edits, agent status revocations (triggers HITL gate).
- `CRITICAL`: System-wide organization deletions, security role grants.

---

## 4. HITL Approval Gate & Security Invariants
- **No Self-Approval**: Requested actor CANNOT approve their own command.
- **Payload Hash Binding**: Every `ApprovalRequest` binds the SHA-256 hash of the command payload. Altering the payload invalidates the approval.
- **Tenant Scoping**: Approver must belong to the exact same organization.

---

## 5. AI Agent Execution Invariant
AI Agents CANNOT bypass the `CommandBus` to access the database or repositories directly. AI Agents propose commands which are strictly validated, policy-checked, risk-assessed, and approved before execution.

---

## 6. Idempotency Engine
Submitting a duplicate command with an `idempotency_key` returns the cached `CommandResult` without re-executing business logic. Submitting the same key with an altered payload hash raises `IdempotencyMismatchError`.
