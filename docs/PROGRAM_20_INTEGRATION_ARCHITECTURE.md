# Program 20: System Integration Architecture

## 1. Global Topology

```text
                 ┌────────────────────────────────────────────────────────┐
                 │                      USER / SPA UI                     │
                 └───────────────────────────┬────────────────────────────┘
                                             │ HTTP / WebSocket
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │                   API GATEWAY ROUTER                   │
                 │      (Rate Limiting, Context Middleware, CORS)         │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │             AUTHENTICATION & TENANCY FILTER            │
                 │      (JWT Validation, Role Binding, Tenant Scoping)    │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │                AGENT RUNTIME & ORCHESTRATOR            │
                 │    (Executive / HR / Employee Specialized AI Agents)   │
                 └─────────────┬───────────────────────────┬──────────────┘
                               │                           │
                 ┌─────────────┴─────────────┐             │
                 ▼                           ▼             ▼
       ┌──────────────────┐        ┌──────────────────┐  ┌──────────────────┐
       │  RAG & KNOWLEDGE │        │   PREDICTIVE ML  │  │  MEMORY HIERARCHY│
       │(Vector Retrieval)│        │ (Calibrated Inf) │  │  (7-Tier Memory) │
       └─────────┬────────┘        └─────────┬────────┘  └─────────┬────────┘
                 │                           │                     │
                 └───────────────────────────┼─────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │             REASONING & TOOL PROPOSAL ENGINE           │
                 │             (Structured Pydantic Decisions)            │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │                 GOVERNED MCP TOOL SERVER               │
                 │   (Capability Authorization, Risk Engine, HITL Gate)   │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                        ┌────────────────────┴────────────────────┐
                        ▼                                         ▼
            [Low Risk: Auto-Execute]                  [High Risk: Escalation]
                        │                                         │
                        │                                         ▼
                        │                             ┌────────────────────────┐
                        │                             │  HUMAN-IN-THE-LOOP     │
                        │                             │    APPROVAL QUEUE      │
                        │                             └───────────┬────────────┘
                        │                                         │ (Human Approves)
                        └────────────────────┬────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │               CQRS COMMAND BUS PIPELINE                │
                 │     (Authoritative State Mutation Execution Gate)      │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │                 UNIT OF WORK & REPOSITORIES            │
                 │         (PostgreSQL 16 + Transactional Outbox)         │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │               EVENT BUS & BACKGROUND WORKERS           │
                 │ (Audit Ledger, Multi-Channel Notifications, WebSockets)│
                 └────────────────────────────────────────────────────────┘
```
