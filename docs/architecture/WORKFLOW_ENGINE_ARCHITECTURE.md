# Technical Architecture Reference — Node 6: Event-Driven Workflow Engine + Durable Job Execution + Scheduler + Recovery Foundation

## 1. Executive Summary & Core Purpose

Node 6 establishes the **asynchronous durable execution backbone** required for autonomous AI agents and enterprise workflows. The engine orchestrates complex multi-step processes, handles failures through exponential backoff and dead-letter queues, persists execution state in PostgreSQL, reclaims crashed worker leases on system restarts, and seamlessly pauses/resumes workflows around Human-In-The-Loop (HITL) approval gates.

---

## 2. Invariant Architecture Principles

### CommandBus-Centric Operations
The Workflow Engine serves strictly as an **orchestrator**. It **NEVER** mutates business data directly via database repositories or services. Every workflow step that performs state mutations MUST execute through the Node 5 `CommandBus` pipeline:

$$\text{Workflow} \rightarrow \text{StepExecutor} \rightarrow \text{Command} \rightarrow \text{CommandBus} \rightarrow \text{PolicyEngine} \rightarrow \text{Authorization} \rightarrow \text{RiskEngine} \rightarrow \text{HITL Gate} \rightarrow \text{ActionExecutor} \rightarrow \text{UnitOfWork} \rightarrow \text{Outbox} \rightarrow \text{Result}$$

### AI Agent Non-Bypass Invariant
Autonomous AI Agents CANNOT bypass the `CommandBus` by executing workflows directly. Commands dispatched during workflow steps undergo full identity resolution, authorization check, dynamic policy evaluation, risk classification, and approval checks.

---

## 3. Core Architecture Subsystems

```
                                      ┌──────────────────────────────┐
                                      │   Domain Events / Ingestion  │
                                      └──────────────┬───────────────┘
                                                     │
                                                     ▼
                                      ┌──────────────────────────────┐
                                      │    EventTriggerProcessor     │
                                      └──────────────┬───────────────┘
                                                     │
                                                     ▼
┌──────────────────────────────┐      ┌──────────────────────────────┐
│  Scheduled Jobs / Scheduler  ├─────►│        WorkflowEngine        │
└──────────────────────────────┘      └──────────────┬───────────────┘
                                                     │ (DAG Step Resolution)
                                                     ▼
                                      ┌──────────────────────────────┐
                                      │         StepExecutor         │
                                      └──────────────┬───────────────┘
                                                     │ (Command Dispatch)
                                                     ▼
                                      ┌──────────────────────────────┐
                                      │    Node 5 Universal          │
                                      │         CommandBus           │
                                      └──────────────┬───────────────┘
                                                     │
                                                     ▼
                                      ┌──────────────────────────────┐
                                      │  ActionExecutor / UoW / DB   │
                                      └──────────────────────────────┘
```

### 1. Workflow Domain Layer (`backend/workflows/domain/`)
- `WorkflowDefinition`: Declarative DAG schema defining steps, dependencies, triggers (`MANUAL`, `COMMAND`, `EVENT`, `CRON`, `DELAY`, `WEBHOOK`), and retry policies.
- `WorkflowExecution`: Stateful runtime instance tracking correlation/causation IDs, input/output payloads, current steps, and lifecycle state (`DRAFT` $\rightarrow$ `READY` $\rightarrow$ `RUNNING` $\rightarrow$ `WAITING` / `WAITING_APPROVAL` $\rightarrow$ `COMPLETED` / `FAILED` / `CANCELLED`).
- `StepExecution`: Granular step execution state tracking attempt counts, output data, error tracebacks, and next retry timestamps.
- `ScheduledJob`: Durable background job persistence tracking worker lease ownership (`lease_owner`, `lease_until`) to eliminate worker race conditions.
- `DeadLetterJob`: Permanent dead-letter record for unrecoverable failures or exhausted retries.

### 2. DAG Execution Engine (`workflow_engine.py` & `definitions.py`)
- **Cycle Detection**: Validates DAG definitions using Kahn's algorithm before saving or executing.
- **Topological Step Sorting**: Computes execution levels allowing independent steps to run concurrently while ensuring dependent steps wait for all prerequisite dependencies to reach `SUCCEEDED` status.
- **Conditional Branching & Skipping**: Automatically skips steps whose prerequisites failed or evaluated negatively.

### 3. Step Execution & CommandBus Integration (`step_executor.py`)
- Constructs deterministic `Command` objects from step definitions and merged execution payloads.
- Preserves idempotency using key format `{workflow_id}-{execution_id}-{step_id}-{attempt}`.
- Dispatches commands strictly via `CommandBus.dispatch(command, context)`.
- Suspends step execution when a command yields `CommandStatus.WAITING_APPROVAL`.

### 4. Retry Engine & Error Classification (`retry_service.py`)
- Classifies failures into `AUTHORIZATION`, `VALIDATION`, `TIMEOUT`, `RATE_LIMITED`, and `RETRYABLE`.
- **Non-Retryable Safety Guarantee**: Authorization and Validation failures are NEVER retried automatically.
- Calculates exponential backoff intervals with random jitter.

### 5. HITL Approval Gate Integration
- When a step triggers a `HIGH`/`CRITICAL` risk command or policy requirement, the workflow transitions to `WAITING_APPROVAL` and emits a `CommandApprovalRequested` event.
- When an authorized approver grants approval via Node 5 `ApprovalService`, `StepExecutor` detects approval status and re-dispatches the command with `CommandStatus.APPROVED`, executing the mutation and completing the workflow step.

### 6. Durable Job Queue & Crash Recovery (`recovery_service.py` & `repositories.py`)
- All jobs, step executions, and workflows persist in PostgreSQL.
- Worker concurrency is governed by database row locks and lease timeouts.
- Upon process crashes or service restarts, `RecoveryService` reclaims expired leases and safely resumes interrupted executions without duplicating completed commands.

---

## 4. Database Schema (`004_workflow_execution_tables.py`)

- `workflow_definitions`: Stores tenant-scoped workflow schemas (`organization_id`, `name`, `version`, `steps_json`, `enabled`).
- `workflow_steps`: Stores individual step definitions and dependency constraints.
- `workflow_executions`: Stores runtime execution status, correlation IDs, and input/output payloads.
- `workflow_step_executions`: Granular execution history per step attempt.
- `scheduled_jobs`: Job queue with `lease_owner` and `lease_until` lease locking columns.
- `dead_letter_jobs`: Stores permanently failed items for inspection and manual replay.

---

## 5. API & CLI Interface Surface

### API v1 Endpoints (`/api/v1/`)
- `/api/v1/workflows`: `POST /`, `GET /`, `GET /{id}`, `POST /{id}/enable`, `POST /{id}/disable`, `DELETE /{id}`
- `/api/v1/workflow-executions`: `POST /`, `GET /{id}`, `POST /{id}/pause`, `POST /{id}/resume`, `POST /{id}/cancel`
- `/api/v1/jobs`: `GET /`, `GET /{id}`
- `/api/v1/dead-letter`: `GET /`, `POST /{id}/discard`

### CLI Tool Commands (`backend/workflows/cli/cli.py`)
- `list_workflows`, `inspect_workflow`
- `list_executions`
- `list_dlq`

---

## 6. Verification & Quality Gates

- **Ruff Linter**: `PASS` (0 errors)
- **Black Formatter**: `PASS` (0 errors across 194 files)
- **MyPy Type Checker**: `PASS` (0 errors across 152 source files)
- **Pytest Suite**: `PASS` (**183 passed**, 2 skipped for offline PostgreSQL)
