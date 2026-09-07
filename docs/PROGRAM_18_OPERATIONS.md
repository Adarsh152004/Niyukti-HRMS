# Program 18: Production Operations, Monitoring & Runbook

## 1. Quickstart & Startup Sequence

```bash
# 1. Activate Environment
.venv\Scripts\activate          # Windows
# or source .venv/bin/activate      # Linux/macOS

# 2. System Verification
python scripts/verify_system.py

# 3. Seed Synthetic Demo Data
python scripts/seed_demo.py --employees 100 --scale medium

# 4. Start FastAPI Gateway
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# 5. Start Frontend SPA
cd frontend && npm run dev
```

---

## 2. Docker Compose Production Deployment

```bash
docker compose build
docker compose up -d
```

Services Managed:
- **`frontend`**: Nginx static build (`http://localhost:80`)
- **`backend`**: FastAPI Gateway (`http://localhost:8000`)
- **`postgres`**: PostgreSQL 16 + pgvector (`localhost:5432`)
- **`redis`**: Redis 7 Cache & Locks (`localhost:6379`)
- **`prometheus`**: Telemetry scraping (`http://localhost:9090`)
- **`grafana`**: Enterprise Dashboards (`http://localhost:3000`)

---

## 3. Observability & Health Endpoints

- **`GET /health`**: Live container and dependency health status (`database`, `redis`, `storage`, `llm`).
- **`GET /ready`**: Kubernetes readiness probe.
- **`GET /metrics`**: Prometheus metrics endpoint (`http_requests_total`, `llm_latency_seconds`, `tokens_consumed_total`).
- **`GET /api/v1/governance/kill-switch/status`**: Current AI fleet operational status.
