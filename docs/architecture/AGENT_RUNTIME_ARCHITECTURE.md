# Technical Architecture Reference — Node 7 Part 1: Autonomous AI Agent Orchestration Layer (Agent Runtime Foundation)

## 1. Executive Summary & Architectural Invariants

Node 7 Part 1 establishes the **Autonomous AI Agent Runtime Foundation** for the enterprise AI-Powered Intelligent HRMS platform.

### Standard Security Invariants

#### LLM $\neq$ Authority
An AI Agent may reason, plan, analyze, select tools, propose actions, create commands, delegate work, and inspect results, but MUST NEVER independently grant itself permissions, capabilities, roles, tenant access, approval authority, or elevated privileges.

#### CommandBus State Mutation Boundary
AI Agents are strictly prohibited from directly mutating business data or accessing database repositories/SQLAlchemy sessions:

$$\text{Agent} \rightarrow \text{AgentCommandGateway} \rightarrow \text{Command} \rightarrow \text{CommandBus} \rightarrow \text{Authorization} \rightarrow \text{PolicyEngine} \rightarrow \text{RiskEngine} \rightarrow \text{HITL Gate} \rightarrow \text{ActionExecutor} \rightarrow \text{UnitOfWork} \rightarrow \text{Outbox} \rightarrow \text{Audit} \rightarrow \text{Result}$$

$$\text{Agent} \not\rightarrow \text{Repository} \quad \text{Agent} \not\rightarrow \text{Database} \quad \text{Agent} \not\rightarrow \text{SQLAlchemy} \quad \text{Agent} \not\rightarrow \text{Direct HRMS Service}$$

---

## 2. Core Concepts & Classification Matrix

| Concept | Security Identity vs Business Role | Responsibility |
| :--- | :--- | :--- |
| **`ActorType.AI_AGENT`** | Security Identity Classification | Authoritative Node 2 & Node 4 security identity for authentication, authorization, and audit logs. |
| **`AgentType`** | Logical Business Classification | Domain responsibility (`SYSTEM_AGENT`, `HR_AGENT`, `RECRUITMENT_AGENT`, `ONBOARDING_AGENT`, `PAYROLL_AGENT`, `COMPLIANCE_AGENT`, `ANALYTICS_AGENT`, `WORKFLOW_AGENT`, `EXECUTIVE_AGENT`, `CUSTOM_AGENT`). |
| **`AgentStatus`** | Lifecycle State | Enforces strict transitions (`CREATED`, `ACTIVE`, `PAUSED`, `SUSPENDED`, `DRAINING`, `DISABLED`, `TERMINATED`). `TERMINATED` is terminal. |
| **`AgentCapability`** | Business Capability Declaration | Runtime boundary (`resource`, `actions`, `risk_level`, `requires_hitl`). Validated prior to CommandBus dispatch. |
| **`AgentTask`** | Task Primitive | Unit of work assigned to an Agent (`goal`, `priority`, `status`, `input`, `output`, `correlation_id`). |
| **`AgentExecutionContext`** | Immutable Execution Token | Token passing Agent identity, mapped `Actor`, tenant `organization_id`, task ID, and capabilities to runtime engines. |
| **`AgentCommandGateway`** | Single Execution Gate | Sole authorized interface for Agents to request state mutations via Node 5 `CommandBus`. |

---

## 3. Agent Lifecycle State Machine

```
                            ┌───────────┐
                            │  CREATED  │
                            └─────┬─────┘
                                  │
                                  ▼
┌───────────┐                ┌───────────┐
│  PAUSED   │◄──────────────►│  ACTIVE   │◄──────────────►┌───────────┐
└─────┬─────┘                └─────┬─────┘                │ SUSPENDED │
      │                            │                      └─────┬─────┘
      │      ┌───────────┐         │                            │
      └─────►│ DISABLED  │◄────────┴────────────────────────────┘
             └─────┬─────┘
                   │
                   ▼
             ┌───────────┐
             │TERMINATED │  (Terminal State)
             └───────────┘
```

---

## 4. Execution Sequence & Gateway Control Flow

```
┌───────┐            ┌─────────────────────┐            ┌────────────────────┐            ┌────────────┐            ┌────────────────┐
│ Agent │            │ AgentCommandGateway │            │ Node 5 CommandBus  │            │ HITL Gate  │            │ ActionExecutor │
└───┬───┘            └──────────┬──────────┘            └─────────┬──────────┘            └─────┬──────┘            └───────┬────────┘
    │                           │                                 │                             │                           │
    │ request_action(...)       │                                 │                             │                           │
    ├──────────────────────────►│                                 │                             │                           │
    │                           │ Validate Agent ACTIVE           │                             │                           │
    │                           │ Validate Tenant Boundary        │                             │                           │
    │                           │ Validate Capability Alignment   │                             │                           │
    │                           │                                 │                             │                           │
    │                           │ dispatch(Command)               │                             │                           │
    │                           ├────────────────────────────────►│                             │                           │
    │                           │                                 │ Authorize Actor             │                           │
    │                           │                                 │ Evaluate Policy & Risk      │                           │
    │                           │                                 │                             │                           │
    │                           │                                 │ High Risk / Approval Req?   │                           │
    │                           │                                 ├────────────────────────────►│                           │
    │                           │                                 │                             │ Create ApprovalRequest    │
    │                           │                                 │◄────────────────────────────┤ Return WAITING_APPROVAL   │
    │                           │                                 │                             │                           │
    │                           │                                 │ Execute Action              │                           │
    │                           │                                 ├────────────────────────────────────────────────────────►│
    │                           │                                 │                             │                           │ Exec Mutation
    │                           │                                 │◄────────────────────────────────────────────────────────┤ Return Result
    │                           │◄────────────────────────────────┤                             │                           │
    │◄──────────────────────────┤                                 │                             │                           │
```

---

## 5. Database Schema & Migration (`005_agent_runtime_foundation.py`)

- `agents`: Stores tenant-scoped AI Agent definitions (`organization_id`, `name`, `status`, `actor_id`, `agent_type`, `capabilities_json`, `metadata_json`).
- `agent_capabilities`: Stores individual capability declarations and risk parameters.
- `agent_tasks`: Stores task execution lifecycle, priorities, inputs, outputs, and correlation IDs.
- `agent_task_events`: Audit trail for agent task execution events.

---

## 6. API v1 & CLI Surface

### API v1 Endpoints (`/api/v1/agents`)
- `POST /`: Register AI Agent
- `GET /`: List AI Agents
- `GET /{id}`: Inspect Agent Details
- `POST /{id}/activate`, `POST /{id}/pause`, `POST /{id}/suspend`, `POST /{id}/disable`, `POST /{id}/terminate`: Lifecycle Actions
- `POST /{id}/tasks`: Create Task
- `GET /{id}/tasks`: List Agent Tasks
- `GET /{id}/tasks/{task_id}`: Inspect Task

### CLI Commands (`backend/agents/cli/cli.py`)
- `agents list`, `agents inspect <id>`, `agents activate <id>`, `agents pause <id>`, `agents tasks <id>`
