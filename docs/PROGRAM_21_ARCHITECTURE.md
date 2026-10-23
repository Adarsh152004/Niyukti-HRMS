# Program 21: System Architecture & Integration Blueprint

## 1. Unified Layered Topology

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             REACT ENTERPRISE SPA UI                         │
│   (Vite + React 18 + TypeScript + TailwindCSS + TanStack Query + Recharts)  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / WebSockets
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI API GATEWAY (BFF)                          │
│          (Middleware: Tenancy, Correlation IDs, Rate Limiting, CORS)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
┌────────────────────────┐ ┌────────────────────────┐ ┌───────────────────────┐
│     QUERY SERVICES     │ │  CQRS COMMAND BUS      │ │   MULTI-PROVIDER      │
│  (Read-Only Projections│ │  (Authoritative State  │ │     AI GATEWAY        │
│   & Analytics Engine)  │ │   Mutation Pipeline)   │ │  (Gemini, Groq, Mock) │
└───────────┬────────────┘ └───────────┬────────────┘ └───────────┬───────────┘
            │                          │                          │
            │                          ▼                          ▼
            │              ┌────────────────────────┐ ┌───────────────────────┐
            │              │   GOVERNANCE ENGINE    │ │ 24 SPECIALIZED AGENTS │
            │              │ (RBAC, Policy & Risk)  │ │ (Supervisor-Worker DAG│
            │              └───────────┬────────────┘ └───────────┬───────────┘
            │                          │                          │
            │                          ▼                          │
            │              ┌────────────────────────┐             │
            │              │  HITL APPROVAL QUEUE   │◄────────────┘
            │              │ (Consequential Actions)│ (High-Risk Proposals)
            │              └───────────┬────────────┘
            │                          │ (Human Approves)
            └──────────────────────────┼──────────────────────────┐
                                       ▼                          ▼
                           ┌────────────────────────┐ ┌───────────────────────┐
                           │    POSTGRESQL 16 UOW   │ │    REDIS 7 CLUSTER    │
                           │  (Relational Tables &  │ │(Distributed Locks,    │
                           │  Transactional Outbox) │ │ Cache, Rate Limiter)  │
                           └───────────┬────────────┘ └───────────────────────┘
                                       │
                                       ▼
                           ┌────────────────────────┐
                           │  EVENT BUS & OUTBOX    │
                           │ (Audit Chain, Notifs,  │
                           │  WebSocket Broadcast)  │
                           └────────────────────────┘
```
