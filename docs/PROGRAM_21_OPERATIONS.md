# Program 21: Operations, Observability & Emergency Runbook

## 1. System Health & Observability Metrics
- **Health Checks**:
  - `GET /health/live`: Basic liveness probe.
  - `GET /health/ready`: Kernel and database readiness probe.
  - `GET /health/dependencies`: Live probe for DB, Redis, Storage, and LLM Router.
- **Correlation IDs**: `X-Correlation-ID` propagated through API requests, agent task context, tool calls, and audit log entries.
- **AI Fleet Kill Switch**:
  - `POST /api/v1/governance/kill-switch/global` with `action="GLOBAL_AI_PAUSE"` halts all agent activities immediately.
  - `POST /api/v1/governance/kill-switch/global` with `action="RESUME"` restores normal agent operations.
