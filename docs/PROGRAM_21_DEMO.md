# Program 21: Demonstration Guide & Persona Playbook

## 1. Quickstart Commands

```bash
# 1. Verify all 25 system components
python scripts/verify_program_21.py

# 2. Seed high-fidelity synthetic demo data
python scripts/seed_demo.py --employees 100 --scale medium

# 3. Execute the 16-step end-to-end demonstration script
python scripts/demo_program_21.py

# 4. Launch Backend API Gateway
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# 5. Launch Frontend Single Page Application
cd frontend && npm run dev
```

---

## 2. Seeded Personas & Credentials
- **CEO / Executive**: `ceo@enterprise.demo` / `Password123!@#Secure`
- **HR Admin**: `admin@enterprise.demo` / `Password123!@#Secure`
- **Employee**: `employee@enterprise.demo` / `Password123!@#Secure`
