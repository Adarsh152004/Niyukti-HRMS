# Program 22: Operations, Deployment & Runbook

## 1. System Launch Commands

```bash
# 1. Complete System Verification
python scripts/verify_program_22.py

# 2. Seed Synthetic Enterprise Data
python scripts/seed_program_22_demo.py --size medium --tenant org-apex-01

# 3. Run Live 24-Step Operational Demonstration
python scripts/demo_program_22.py

# 4. Launch Backend API Gateway
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# 5. Launch Frontend SPA
cd frontend && npm run dev
```
