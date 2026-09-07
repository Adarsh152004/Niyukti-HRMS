# Program 22: System Architecture & End-to-End Operational Pipeline

## 1. Global System Topology

```text
                         ┌──────────────────────┐
                         │     Human User       │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ React Enterprise UI  │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ API / WebSocket      │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Auth + Tenant        │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────▼────────────────┐
                   │ AI / Command Runtime             │
                   │                                  │
                   │ Context + Memory + RAG           │
                   │ LLM Gateway + Guardrails         │
                   │ Agent Runtime + Supervisors      │
                   │ MCP + Tool Registry              │
                   └────────────────┬─────────────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Governance Plane     │
                         │                      │
                         │ Authorization        │
                         │ Policy Engine        │
                         │ Risk Engine          │
                         │ HITL                 │
                         │ Kill Switch          │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ CommandBus           │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ HR Domain Services   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ UnitOfWork           │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ PostgreSQL/pgvector  │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Transactional Outbox │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Event Bus / Workers  │
                         └─────┬─────────┬──────┘
                               │         │
                    ┌──────────▼───┐ ┌──▼─────────────┐
                    │ Notifications│ │ KPI / ML /    │
                    │ Email/WA/etc │ │ Analytics     │
                    └──────────────┘ └──────┬─────────┘
                                            │
                                  ┌─────────▼─────────┐
                                  │ WebSocket / UI    │
                                  └───────────────────┘
```
