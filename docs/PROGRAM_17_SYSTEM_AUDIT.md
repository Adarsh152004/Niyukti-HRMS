# Program 17: Full System Architectural & Codebase Audit

**Date**: August 2026  
**System**: AI-Powered Intelligent HRMS Platform  
**Target**: Complete AI-Native System Integration & Productionization  

---

## 1. Executive Summary & Existing Architecture (Programs 1–16)

Across Programs 1 through 16, the repository has established a comprehensive enterprise foundation:
1. **Domain Layer (Hexagonal / Clean Architecture)**: 14 core HRMS domains (Organization, Employee, Attendance, Leave, Payroll, Recruitment, Performance, Learning, Documents, Policies, Approvals, Analytics, Skills, Designations) with immutable Value Objects and Domain Exceptions.
2. **Command Bus & CQRS**: Dynamic Command Bus with RBAC/ABAC authorization checks, Risk Engine, Policy Engine, and transactional UnitOfWork boundaries.
3. **Event-Driven & Outbox Architecture**: In-memory and PostgreSQL Transactional Outbox workers with asynchronous event publishing, dead-letter queue (DLQ) routing, and exponential backoff.
4. **Agentic AI & Autonomy Runtime**:
   - 24 Specialized HR Agent Roles (CEO/Executive HR, Talent Acquisition, Resume Screening, Payroll Assistant, Attrition Predictor, etc.).
   - Autonomy Levels (L0 Manual $\to$ L4 Full Autonomy) and Human-in-the-Loop (HITL) dual-approval governance.
   - Supervisor-Worker hierarchy with capability intersection and recursive delegation protection.
5. **Workflow & Saga Orchestration**: 20 pre-built enterprise workflow templates (Onboarding, Offboarding, Payroll Batch, Promotion, etc.) with compensating saga steps.
6. **Machine Learning Intelligence**: ML Domain models for Attrition Prediction, Resume Screening, and Market Compensation with Expected Calibration Error (ECE $\le 0.05$), Brier scoring, and PSI concept drift monitoring.
7. **Security, Privacy & Audit**:
   - Cryptographic SHA-256 hash-chain audit ledger with tamper detection.
   - GDPR Article 15 (DSAR Export) & Article 17 (Right to Erasure) automated pipelines.
   - SOC 2 Type II and ISO 27001 automated compliance rules evaluators.
8. **Frontend & UI**: 19-page React 18 / Vite / Tailwind / Radix UI SPA with 70 design tokens, command palette (`cmdk`), theme switcher, and responsive data tables.
9. **API Gateway & Real-Time**: FastAPI gateway with Request Context (Correlation ID & Multi-Tenancy), Sliding-Window Rate Limiting, Real-time WebSockets (`/ws/*`), SSE streams (`/api/v1/ai/stream`), and GraphQL endpoint (`/graphql`).
10. **Infrastructure & Deployment**: Multi-stage Dockerfiles (non-root `appuser:10001` / `nginx`), Kubernetes HA manifests (HPA, PDB, Ingress), GitHub Actions CI/CD pipelines, and Prometheus/Grafana configs.

---

## 2. Reusable Components & Modules

| Component Area | Existing Location | Reusability Plan |
|---|---|---|
| Domain Models | `backend/hrms/domain/` | Fully reused as core domain entities and invariants. |
| Command Bus | `backend/commands/` | Primary mutation gateway for both human and agent actions. |
| Event Bus & Outbox | `backend/events/` | Drains domain events and distributes real-time notifications. |
| Agent Roster & Base | `backend/agents/` | Runtime for 24 specialized HR agents and supervisor-worker delegation. |
| Governance & Guardrails | `backend/governance/` | Content filter, risk engine, HITL approval queue, emergency kill-switches. |
| ML Calibration | `backend/ml/calibration/` | ECE, Brier, PSI drift, and algorithmic fairness validation. |
| Cryptographic Audit | `backend/security/audit/` | Immutable SHA-256 hash-chain audit trail. |
| Frontend SPA | `frontend/src/` | 19 React pages, UI components, and API query hooks. |
| Database Seeder | `backend/database/seeder/` | Synthetic data generators for 100+ employees and multi-domain graphs. |

---

## 3. Gaps, Missing Integrations & Production Blockers

1. **Redis Infrastructure Abstraction**:
   - Need unified `backend/infrastructure/redis/` with `client.py`, `cache.py`, `locks.py`, `rate_limit.py`, and `idempotency.py` supporting both live Redis instances and graceful local in-memory fallbacks.
2. **Object Storage Abstraction**:
   - Need `backend/storage/` with `StoragePort`, `LocalStorage`, and `S3CompatibleStorage` for document, resume, and payslip binary storage with signed URLs and tenant isolation.
3. **Unified Authentication & Identity Management**:
   - Complete `/api/v1/auth` routes (`/login`, `/refresh`, `/logout`, `/me`) integrating JWT access & refresh tokens, password hashing, and tenant role/permission context.
4. **Real Multi-Provider LLM Gateway**:
   - Implement `LLMProvider` interface with concrete adapters for OpenAI, Anthropic, Gemini, and deterministic Offline/Mock providers with fallback failover.
5. **Context Window Management**:
   - Implement `backend/agents/context/` (`budget.py`, `compressor.py`, `summarizer.py`, `selector.py`) for explicit token budgeting across system, memory, RAG, and tool results.
6. **Governed MCP Tool Architecture**:
   - Build `backend/mcp/` (`server.py`, `registry.py`, `schemas.py`, `security.py`, `transport.py`) wrapping existing `ToolRegistry` with capability verification and CommandBus routing.
7. **Analytics & KPI Engine**:
   - Create `backend/analytics/` (`KPIService`, `MetricsService`, `DashboardService`, `ReportService`) delivering live aggregations from real database data.
8. **Interactive AI Command Center**:
   - End-to-end endpoint `/api/v1/ai/command` enabling natural language operations (e.g., "Show employees with attendance below 85%", "Start onboarding for Rahul") with reasoning, tool execution, and HITL gate creation.
9. **Automated Verification Scripts & CI/CD Bootstrap**:
   - `scripts/bootstrap.py`, `scripts/seed_demo.py`, and `scripts/verify_system.py`.

---

## 4. Recommended Integration Sequence

```
1. Infrastructure & Storage (Redis, Object Storage)
       ↓
2. Authentication, RBAC/ABAC & Identity Wiring
       ↓
3. LLM Gateway & Multi-Provider Router (OpenAI, Anthropic, Gemini, Mock)
       ↓
4. Context Window & Memory Hierarchy Management
       ↓
5. MCP & Tool Calling Architecture Integration
       ↓
6. AI Command Center & End-to-End Reasoning Runtime
       ↓
7. KPI & Analytics Engine Integration
       ↓
8. Synthetic Demo Seeder & End-to-End Scenarios
       ↓
9. Comprehensive Testing Suite (E2E, Security, RAG, MCP, HITL)
       ↓
10. Final Verification & Documentation (Runbooks, Security Models, Final Report)
```
