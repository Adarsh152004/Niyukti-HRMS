# Program 22: Observability, Metrics & Telemetry

## 1. Metrics & Probes
- **Probes**:
  - `GET /health/live`: Basic liveness probe.
  - `GET /health/ready`: Database and core subsystem readiness.
  - `GET /health/dependencies`: Probes PostgreSQL, Redis, Object Storage, and LLM Multi-Provider Gateway.
- **Trace Propagation**: `X-Correlation-ID` header injected on request entry and propagated through AI Gateway, Governed MCP Tools, CommandBus, and SHA-256 Audit Trail.
