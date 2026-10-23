# Program 17: Production Operations & Runbook

## 1. Quickstart & Local Execution

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16 (optional for demo, memory-mode supported)
- Redis 7 (optional for demo, memory-mode supported)

### Step 1: Initialize Virtual Environment & Dependencies
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# or source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

### Step 2: Bootstrap & Seed Demo Data
```bash
python scripts/bootstrap.py
python scripts/seed_demo.py --employees 100 --scale medium
```

### Step 3: Run Backend API Gateway
```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Run Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173/`.

---

## 2. Production Docker Deployment

```bash
docker compose up --build -d
```
Services started:
- **Frontend SPA**: `http://localhost:80`
- **Backend API Gateway**: `http://localhost:8000/api/docs`
- **PostgreSQL (`pgvector`)**: `localhost:5432`
- **Redis Cache**: `localhost:6379`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000`

---

## 3. Operations & Maintenance CLI Commands

### Database Seeding
```bash
python -m backend.database.seed --scale small|medium|large --tenant-id org-apex-01
```

### Continuous Calibration & Calibration Gate
```bash
python -m backend.ml.calibration.cli --output-report reports/CALIBRATION_REPORT.md
```

### Security, GDPR & SOC 2 Compliance Audit
```bash
python -m backend.governance.compliance.cli --output-report reports/SOC2_GDPR_COMPLIANCE_REPORT.md
```

### System Health Verification
```bash
python scripts/verify_system.py
```
