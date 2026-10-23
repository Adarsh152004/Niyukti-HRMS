# Program 17: Canonical AI-Native System Architecture

## Architectural Invariant

$$\mathbf{LLM \neq AUTHORITY}$$

AI agents may reason, analyze, summarize, classify, retrieve, recommend, plan, propose actions, select approved tools, delegate bounded tasks, and request human approval.

AI must **never** directly mutate the database, execute arbitrary code or shell commands, bypass authorization or policies, grant itself capabilities, or approve its own high-risk actions.

---

## Unified End-to-End System Flow

```text
                    ┌───────────────────────────┐
                    │ React / TypeScript UI     │
                    │ HRMS + AI Command Center  │
                    └─────────────┬─────────────┘
                                  │
                        REST / WebSocket / SSE
                                  │
                    ┌─────────────▼─────────────┐
                    │ FastAPI API Gateway       │
                    │ Auth / Rate Limit         │
                    │ Idempotency / Validation  │
                    └─────────────┬─────────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
        HRMS APIs             AI Gateway          WebSocket
             │                    │
             │              ┌─────▼─────┐
             │              │ LLM Router│ (OpenAI / Anthropic / Gemini / Mock)
             │              └─────┬─────┘
             │                    │
             │              Reasoning Engine (Structured Pydantic Output)
             │                    │
             │              Context Builder (Token Budgeting & Compression)
             │                    │
             │              Memory + RAG (Vector Search & Knowledge Store)
             │                    │
             │              Tool Registry (Governed Domain Tools)
             │                    │
             │              MCP Adapter (Model Context Protocol Standard)
             │                    │
             │              Agent Command Gateway
             │                    │
             └──────────────┬─────┘
                            │
                        CommandBus (Dynamic Dispatcher)
                            │
                 ┌──────────┼──────────┐
                 ▼          ▼          ▼
              Auth       Policy       Risk
                 │          │          │
                 └──────────┼──────────┘
                            │
                         HITL Gate (Human-in-the-Loop for High Risk)
                            │
                       Domain Services (Deterministic Business Logic)
                            │
                         UnitOfWork (ACID Transaction Boundary)
                            │
                       PostgreSQL (Relational + pgvector)
                            │
                   Transactional Outbox
                            │
                        Event Bus
                     ┌──────┼──────┐
                     ▼      ▼      ▼
                   Audit  Worker  Notifications
```

---

## Core System Subsystems

1. **API & Real-Time Gateway**: REST API v1 endpoints, GraphQL schema, WebSockets (`/ws/events`), and Server-Sent Events (`/api/v1/ai/stream`).
2. **Infrastructure Layer**: PostgreSQL with `pgvector`, Redis for caching, rate limiting, and distributed locking, and Object Storage for binary file storage.
3. **Security & Identity**: JWT Bearer authentication, API key authentication, RBAC + ABAC authorization, and cryptographic hash-chain audit ledger.
4. **AI & Multi-Agent Runtime**: 24 specialized HR agent roles, Supervisor-Worker coordination, explicit context token budgeting, multi-tiered memory hierarchy, and governed tool execution.
5. **Human-in-the-Loop (HITL) Center**: Dual-control approval workflows with expiration timeouts, evidence inspection, and audit logging.
6. **Machine Learning Center**: Predictive inference for Attrition, Resume Screening, and Market Compensation with Expected Calibration Error (ECE $\le 0.05$) and PSI drift monitoring.
7. **Continuous Observability**: Prometheus scrape metrics, Grafana dashboards, OpenTelemetry correlation IDs, and emergency kill-switches.
