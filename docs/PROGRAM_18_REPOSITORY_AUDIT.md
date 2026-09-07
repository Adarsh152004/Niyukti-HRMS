# Program 18: Complete Repository Architecture & Subsystems Audit

**Date**: August 2026  
**System**: AI-Powered Intelligent HRMS (Enterprise Edition)  
**Status**: Comprehensive Baseline Audit & Production Activation Mapping  

---

## 1. Executive Summary & Inventory

The repository is built upon a layered, domain-driven architecture established across Programs 1 through 17. The system enforces the fundamental governance invariant:

$$\mathbf{LLM \neq AUTHORITY}$$

All AI mutations must pass through structured Pydantic extraction, governed MCP capability checks, the CQRS CommandBus, policy and risk engines, Human-in-the-Loop (HITL) gates, and UnitOfWork to PostgreSQL with transactional outbox and cryptographic audit logging.

### Subsystems Audit Matrix

| # | Subsystem | Entry Point | Core Dependencies | Persistence Model | API Surface | Frontend Integration | AI Integration | Missing Production Wiring / Gap | Risk Level | Recommended Program 18 Action |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **Core HRMS Domain (14 Modules)** | `backend/hrms/` | Domain Entities, Service Layer | `InMemoryRepositories` & `SQLAlchemy` models | `/api/v1/employees`, `/departments`, `/attendance`, `/leave`, `/payroll`, `/recruitment`, `/performance`, `/learning`, `/policies`, `/approvals`, `/reports` | Full React router routes + TanStack Query hooks | Governed MCP Tools (`attendance.summary`, `employee.get`, `payroll.update_salary`) | Database repository factory dynamically toggling memory/Postgres connection pooling | LOW | Complete PostgreSQL UoW wiring with tenant-filtered session bindings |
| **2** | **CQRS CommandBus & UoW** | `backend/commands/` | `CommandBus`, `UnitOfWork` | Transactional Outbox, PostgreSQL | `/api/v1/commands/dispatch` | Command triggers via mutation hooks | AI Tool Proposal $\to$ CommandBus | Wire all 14 domain command handlers to transactional unit of work | LOW | Ensure all high-risk tool proposals route directly through CommandBus |
| **3** | **Security & Auth** | `backend/security/` | `JWTService`, `AuthenticationService`, `RBACPolicy` | `IdentityRepository`, `SessionRepository` | `/api/v1/auth/register`, `/login`, `/refresh`, `/logout`, `/me`, `/api-keys` | AuthContext, Token interceptor, protected routes | Autonomous Agent independent identities, zero human impersonation | Add complete role separation (CEO, HR_ADMIN, MANAGER, EMPLOYEE, AUDITOR, AI_OPERATOR) | LOW | Enforce strict RBAC + ABAC tenant authorization on all endpoints |
| **4** | **Redis Infrastructure** | `backend/infrastructure/redis/` | `RedisClient`, `CacheManager`, `DistributedLock`, `RedisRateLimiter`, `IdempotencyManager` | Redis 7 + Thread-safe in-memory fallback | Middleware rate limiter, Idempotency headers | Automatic retry & headers | Session/cache keying, agent coordination locks | Namespace isolation with organization keys | LOW | Fully wire sliding-window distributed limiter & idempotency storage |
| **5** | **Object Storage** | `backend/storage/` | `StoragePort`, `LocalStorage`, `S3CompatibleStorage` | Local filesystem / S3-compatible buckets | `/api/v1/documents/upload`, `/download` | Document library UI | Document intelligence extraction, resume screening | Integrate MIME validation, path traversal sanitization, signed URLs | LOW | Complete secure signed-URL generation for payslips, resumes & policies |
| **6** | **Multi-Provider LLM Gateway** | `backend/ai/providers/` | `LLMRouter`, `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`, `MockLLMProvider` | Ephemeral telemetry | `/api/v1/ai/command`, `/api/v1/ai/chat` | AI Workspace Chat, Command Palette, Assistant Bar | Multi-tier failover, structured Pydantic `ReasoningDecision` | Wire environment-driven fallback cascade with timeout & token accounting | LOW | Enforce strict Pydantic parsing and token budgets |
| **7** | **Context & Token Budgeting** | `backend/agents/context/` | `ContextBudgetManager`, `ContextCompressor` | In-memory token accountant | Internal agent context builder | Status badge & token count telemetry | 8,192 token window partition across System, Memory, Citations, Tools, User | Enforce priority context selection & eviction of low-value memory | LOW | Active context trimming on all multi-turn conversation endpoints |
| **8** | **Memory Hierarchy** | `backend/agents/memory/` | `MemoryService`, `MemoryStore` | Tiered memory store | `/api/v1/memory/` | Agent memory explorer | Working, Task, Episodic, Semantic, Organization memory | Strict tenant and agent memory scope boundary enforcement | LOW | Enforce cross-agent memory isolation rules |
| **9** | **Knowledge / RAG Brain** | `backend/knowledge/` | `KnowledgeEngine`, `DocumentParser`, `VectorStore` | Vector index (`pgvector` / memory) | `/api/v1/knowledge/search`, `/documents/index` | Document explorer, citation popovers | Policy QA, resume-job semantic matching with citations | Enforce citation verification: Document, Version, Page, Chunk ID | LOW | Ground all AI policy answers with strict verifiable citations |
| **10** | **Governed MCP Tool Server** | `backend/mcp/` | `GovernedMCPServer`, `ToolRegistry` | In-memory governed registry | Internal MCP dispatch & `/api/v1/ai/command` | Tool execution indicators | 14 governed domain tools with capability authorization & HITL gate | Automatic HITL approval generation on high-risk mutation proposals | LOW | Ensure zero raw SQL, shell, or self-approval permissions for AI tools |
| **11** | **24 Specialized Agents & Supervisor** | `backend/agents/specialized/` | 24 HR Agents, Supervisor Catalog | `AgentExecutionLedger` | `/api/v1/agents/`, `/specialized-agents/` | Agent Fleet Center, Live Task Timeline | Multi-agent DAG delegation, bounded recursion, SLA enforcement | Enforce supervisor capability intersection and delegation timeouts | LOW | Implement explicit supervisor-worker workflows for Recruitment & Workforce |
| **12** | **HITL Approval Engine** | `backend/governance/hitl.py` | `ApprovalInboxService`, `HITLGate` | `ApprovalRepository`, Hash-chain ledger | `/api/v1/approvals/` | HITL Approval Center UI (`/approvals`) | High-risk AI tool proposal interception and human review | Cryptographic linkage between human approval and executed CommandBus mutation | LOW | Full interactive Approve/Reject UI with audit trail verification |
| **13** | **Analytics & KPI Engine** | `backend/analytics/` | `KPIService`, `MetricsService` | Domain aggregation queries | `/api/v1/analytics/dashboard`, `/departments`, `/ai-ops` | Executive Dashboard, Analytics charts, CEO Command Center | AI summary of workforce trends, attrition explanations | Connect live database queries for headcount, attendance, payroll, AI ops | LOW | Replace hardcoded mock fallbacks with live aggregate metrics |
| **14** | **Predictive ML Platform** | `backend/ml/` | `ContinuousEvaluationRunner`, `CalibrationHarness` | Model registry & lineage DAG | `/api/v1/ml/` | ML Insights UI, Retention risk badges | Attrition prediction, performance forecasting, candidate ranking | ML predictions must never mutate state directly; require human review | LOW | Connect ML feature extractors and lineage trackers to HR flows |
| **15** | **EventBus & Transactional Outbox** | `backend/events/` | `EventBus`, `OutboxPublisherWorker`, `DeadLetterQueue` | Transactional Outbox table | Internal event subscribers & `/api/v1/dlq` | Event notifications | Async event-driven workflow step advancement | Background outbox drain worker with exponential backoff & DLQ | LOW | Ensure idempotent event consumers with deduplication keys |
| **16** | **Cryptographic Audit Chain** | `backend/security/audit/` | `CryptoChainLedger`, `ComplianceEvaluator` | Append-only SHA-256 Hash Chain | `/api/v1/audit/`, Compliance CLI | Audit & Lineage Explorer UI | Decision lineage tracking and tamper detection | Automatic hash-chain recording on every CommandBus execution | LOW | Complete audit record explorer with masked sensitive fields |
| **17** | **Frontend Single Page App** | `frontend/src/` | React 18, TypeScript, TailwindCSS, Vite, TanStack Query | Client state | Browser UI (`http://localhost:5174/`) | Full design system with dark/light mode | AI Command Center, Workspace Chat, Agent Fleet, Approvals | Connect real backend REST API endpoints across all views | LOW | Remove fixture-only mocks from production execution paths |
| **18** | **Production Infra & CI/CD** | `docker/`, `deploy/` | Multi-stage Dockerfiles, K8s, Prometheus, Grafana | Container runtimes | Health endpoints (`/health`, `/ready`, `/live`, `/metrics`) | System status | Telemetry metrics scraping | Ensure clean compose health checks without sleep commands | LOW | Full automated verification of container health & readiness |

---

## 2. Invariant & Governance Verification

### Non-Negotiable Principle: $\text{LLM} \neq \text{AUTHORITY}$
1. **Zero Raw SQL/Shell Execution**: No LLM prompt or agent execution can execute raw database queries, shell scripts, or OS commands.
2. **Capability Check**: Every tool call is authenticated against the agent's least-privilege capability scope.
3. **HITL Interception**: Any mutation categorized as `HIGH` or `CRITICAL` risk (e.g. salary adjustment, employee termination, bulk payroll finalization) **MUST** halt and generate a `HITLApprovalRequest`.
4. **Tenant Isolation**: Every database query, cache key, vector search, file access, and WebSocket broadcast strictly partitions by `tenant_id` (`organization_id`).

---

## 3. Program 18 Production Activation Strategy

We execute Program 18 through 31 systematic steps:
- **Phase 1: Persistence & Core Infrastructure Activation** (Database, Redis, Storage, Security, Tenant Isolation, API Contracts).
- **Phase 2: AI & Agentic Governance Activation** (Multi-Provider Gateway, MCP, Agent Runtime, Context/Memory, RAG Brain, HITL Gate, Analytics, ML).
- **Phase 3: End-to-End Business Flows & Supervisors** (Recruitment, Onboarding, Leave, Attendance, Payroll, Performance, Document Intelligence, Supervisor-Worker DAGs).
- **Phase 4: Real-Time, Observability & Background Workers** (Outbox Worker, WebSockets, Notifications, Observability, Resilience, Scheduler).
- **Phase 5: Frontend Productization & UI Polish** (Real API Wiring, Design System, Executive Dashboard, Employee 360, Agent Fleet UI, HITL UI, AI Command Center).
- **Phase 6: E2E Scenarios, Adversarial Security & Quality Gates** (14 Golden E2E Scenarios, Adversarial Defense, Docker Verification, Final Regression & Report).
