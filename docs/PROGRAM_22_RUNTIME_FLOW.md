# Program 22: Complete Runtime Flow & Event Propagation

## 1. Traceable Operational Flow

```text
A user performs an action in the UI.
    ↓
The request reaches the actual API.
    ↓
Authentication is verified (JWT PBKDF2).
    ↓
Tenant isolation is enforced (org-apex-01).
    ↓
Authorization is evaluated (RBAC/ABAC).
    ↓
[If AI is involved]:
    context is constructed
    ↓
    memory retrieved (7-tier hierarchy)
    ↓
    authorized RAG retrieval (pre-retrieval role check)
    ↓
    prompt firewall (injection neutralization)
    ↓
    context budget (8,192 token limit)
    ↓
    LLM provider (Gemini / Groq / Mock)
    ↓
    structured output validation (ReasoningDecision)
    ↓
    guardrails & tool proposal
    ↓
[If a tool is required]:
    MCP / tool registry (14 governed tools)
    ↓
    capability check & policy check
    ↓
    risk classification
    ↓
    HITL if required (approval request generated)
    ↓
    CommandBus (authoritative state mutation)
    ↓
    domain service & Unit of Work
    ↓
    PostgreSQL 16 relational commit
    ↓
    transactional outbox event
    ↓
[Async Propagation]:
    event bus & background workers
    ↓
    notifications & audit trail
    ↓
    KPI / analytics update
    ↓
    WebSocket event broadcast
    ↓
    Real-time UI update
```
