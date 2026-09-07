# Production-Grade REST & GraphQL API Gateway Architecture (Node 12)

## Overview
The API Gateway layer is the hardened perimeter bridging frontend client applications, autonomous agent runtimes, background event consumers, and external webhooks to the governed HRMS application core.

---

## 1. Gateway Security & Multi-Tenancy Layer

### A. Context Extraction (`RequestContextMiddleware`)
- **Correlation ID**: Extracts `X-Correlation-ID` or generates a unique `corr-<hex>` ID attached to all logs, events, and response headers.
- **Tenant Context**: Extracts `X-Tenant-ID` or query parameter, binding `tenant_id_ctx` across all async execution branches.
- **Client IP & User Agent**: Recorded for rate limiting and audit lineage.

### B. Authentication & Token Verification (`AuthPrincipal`)
1. **OAuth2 / OIDC Bearer Tokens**:
   - Cryptographically verified JWTs (HMAC-SHA256 / RSA256).
   - Embedded claims: `sub` (user_id), `tenant_id`, `roles`, `scopes`, `risk_tier`.
2. **API Keys**:
   - `X-API-Key` headers (`ak_live_*`, `ak_test_*`) for autonomous agents, background daemons, and programmatic CLI access.
3. **RBAC & ABAC Enforcement**:
   - `@require_roles(*roles)` FastAPI dependency verifying role possession with hierarchy support (`ADMIN`, `EXECUTIVE`, `HR_MANAGER`, `EMPLOYEE`, `AGENT`).

---

## 2. Sliding-Window Rate Limiting & DoS Protection (`RateLimitMiddleware`)

- **Algorithm**: Sliding window timestamp log with automatic microsecond pruning.
- **Tiered Quotas**:
  - `Standard User`: 60 requests/min
  - `Authenticated User / Manager`: 300 requests/min
  - `Executive / Admin`: 600 requests/min
  - `Autonomous Agent / System Worker`: 1,200 requests/min
- **Response Protocol**:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining quota in current window
  - `X-RateLimit-Reset`: Unix epoch timestamp when quota fully resets
  - On limit exceeded: HTTP 429 Too Many Requests with `Retry-After: <seconds>` header and structured error envelope.

---

## 3. Real-Time Streaming & WebSockets (`/ws/*` & `/api/v1/ai/stream`)

### A. Multi-Tenant WebSocket Hub (`WebSocketHub`)
- Multi-channel subscription model:
  - `tenant:{tenant_id}`: Live system alerts, compliance notifications, and approval requests.
  - `workflow:{workflow_id}`: Real-time DAG step transitions and human gate prompts.
  - `agent:{agent_id}`: Live agent thought streams, reasoning traces, and tool execution status.

### B. Server-Sent Events (SSE) AI Streaming
- `GET /api/v1/ai/stream?prompt=...`:
  - `event: tool_execution` — Observable tool invocation and policy verification stages.
  - `event: message` — Token chunk streaming.
  - `event: done` — Structured completion metadata, calibrated confidence score, and policy citation references.

---

## 4. Unified GraphQL Relational Gateway (`/graphql`)

- Schema SDL:
  - `Employee` 360 graph with relational Department, Manager, Direct Reports, and verified Skills.
  - `Agent` fleet hierarchy and operational success metrics.
  - `Organization` summary KPIs.
- Introspection & query explorer available on `/graphql`.

---

## 5. Transactional Outbox Background Publisher (`OutboxPublisherWorker`)

- **Pattern**: Transactional Outbox with asynchronous polling drain.
- **Reliability**: At-least-once delivery to distributed event bus with exponential backoff on transient transport errors.
- **Dead Letter Queue**: Events exceeding maximum retry budget are routed to DLQ with detailed failure metadata.
