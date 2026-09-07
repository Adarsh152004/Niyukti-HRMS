# Program 20: Operations, Observability & Deployment Runbook

## 1. System Observability & Telemetry Metrics

- **API Metrics**: Requests/sec, p50/p95/p99 latency, HTTP 4xx/5xx error rates.
- **LLM Gateway**: Input/output tokens, provider costs (USD), prompt latency, fallback counters.
- **Agent Runtime**: Task execution duration, tool call count, delegation depth, SLA breaches.
- **Governed MCP & HITL**: Approval request wait time, approval vs rejection rates, risk distribution.
- **Database & Redis**: Active connection pool, query duration, Outbox backlog size, Redis cache hit ratio.

---

## 2. Emergency Operations

### Global AI Fleet Kill-Switch
To immediately halt all autonomous agent actions across the organization:
```bash
curl -X POST http://localhost:8000/api/v1/governance/kill-switch/global \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action": "GLOBAL_AI_PAUSE", "reason": "Operational maintenance emergency freeze"}'
```

### Resume AI Fleet Operations
```bash
curl -X POST http://localhost:8000/api/v1/governance/kill-switch/global \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action": "RESUME", "reason": "Maintenance complete"}'
```
