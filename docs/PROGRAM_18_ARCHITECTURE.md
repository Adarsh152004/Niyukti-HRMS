# Program 18: Single Integrated System Architecture

## 1. System Topology & Data Flow

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND ENTERPRISE CLIENT SPA                             │
│       React 18 + TypeScript + Tailwind CSS + TanStack Query + WebSocket Streaming       │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                       HTTPS REST / GraphQL / WSS Realtime
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED FASTAPI GATEWAY & MIDDLEWARE                            │
│  - Correlation ID Middleware (X-Correlation-ID)                                        │
│  - Multi-Tenant Isolation Middleware (X-Tenant-ID claim validation)                    │
│  - Rate Limiting Middleware (Sliding Window Redis)                                     │
│  - Idempotency Middleware (X-Idempotency-Key)                                          │
│  - Authentication & RBAC/ABAC Guard (JWT Access/Refresh + API Keys)                    │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         │                                 │                                 │
         ▼                                 ▼                                 ▼
┌───────────────────────┐       ┌───────────────────────┐       ┌────────────────────────┐
│   CORE HRMS DOMAIN    │       │     AI WORKSPACE      │       │  ANALYTICS & ML ENGINE │
│  - 14 Domain Modules  │       │  - Multi-Provider LLM │       │  - Real-time KPIs      │
│  - Employee 360       │       │  - Context Budgeting  │       │  - Attrition Predictor │
│  - Attendance Ledger  │       │  - Prompt Firewall    │       │  - Performance Predict │
│  - Leave Engine       │       │  - Structured Output  │       │  - ECE Calibration     │
│  - Payroll Engine     │       │  - RAG / Citations    │       │  - Decision Lineage    │
│  - Recruitment / ATS  │       │  - Governed MCP Tools │       │  - Fairness Auditing   │
└───────────────────────┘       └───────────────────────┘       └────────────────────────┘
         │                                 │                                 │
         │                      Tool Execution / Mutation                    │
         │                                 │                                 │
         └─────────────────────────────────┼─────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            CQRS & GOVERNANCE PIPELINE                                  │
│  1. CommandBus.dispatch(Command)                                                       │
│  2. PolicyEngine.evaluate(PolicyContext)                                               │
│  3. RiskEngine.score(Command)                                                          │
│  4. HITL Gate: If Risk >= HIGH -> Suspend & Queue ApprovalRequest -> Await Human       │
│  5. CommandHandler.handle(Command, UnitOfWork)                                         │
│  6. UnitOfWork.commit() -> PostgreSQL Database + Staged Outbox Events                  │
│  7. Transactional Outbox Worker -> EventBus -> Event Subscribers                       │
│  8. Cryptographic Hash-Chain Audit Ledger (SHA-256 Tamper-Evident Chain)                │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             INFRASTRUCTURE & PERSISTENCE                               │
│  - PostgreSQL 16 + pgvector (ACID Relational Models + Vector Embeddings)               │
│  - Redis 7 (Distributed Cache, Lock Management, Rate Limiting, Idempotency)            │
│  - Object Storage (Local File System / S3-Compatible Buckets + Signed URLs)             │
│  - Background Workers (Outbox Publisher, Document Intelligence, DLQ Recovery)          │
│  - Observability (Prometheus Metrics Scraper + Grafana Enterprise Dashboards)          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Invariant Guarantee: $\text{LLM} \neq \text{AUTHORITY}$

1. **Structured Output**: AI decisions must serialize to Pydantic `ReasoningDecision` models.
2. **Capability Check**: MCP tools require explicit role capabilities (`ATTENDANCE_READ`, `PAYROLL_WRITE`, etc.).
3. **HITL Interception**: Autonomous mutations affecting financial, contractual, or termination data are gated by human confirmation.
4. **Deterministic Math**: Payroll calculations, leave accruals, and tax rules execute in deterministic domain engines.
