# Program 20: Comprehensive System Demonstration Guide

## 1. Quick Launch Steps

```bash
# Step 1: Run System Verification (All 25 Subsystems)
python scripts/verify_system.py

# Step 2: Seed High-Fidelity Enterprise Demo Data
python scripts/seed_demo.py --employees 100 --scale medium

# Step 3: Launch Live System Demonstration Script
python scripts/demo_ai_hrms.py

# Step 4: Launch Backend API Gateway
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# Step 5: Launch Frontend Single Page Application
cd frontend && npm run dev
```

---

## 2. Interactive UI Walkthrough Scenarios

### Persona 1: CEO / Executive (`ceo@enterprise.demo` / `Password123!@#Secure`)
1. **Executive Dashboard**: Review organization-wide metrics (Headcount: 128, Attendance: 94.6%, Monthly Spend: $1.24M).
2. **AI Command Chat**: Ask *"What are our top workforce risks and attendance anomalies?"*. Review structured citations and interactive chart cards.
3. **Pending Approvals Queue**: Navigate to `/approvals` to review and sign off on high-risk compensation and headcount adjustments.

### Persona 2: HR Manager (`admin@enterprise.demo` / `Password123!@#Secure`)
1. **Employee 360 Portal**: Navigate to `/employees` to inspect profiles, tenure, and department allocations.
2. **Candidate Recruitment Pipeline**: Navigate to `/recruitment` to view job requisitions and candidate match rankings.
3. **Emergency AI Kill-Switch**: Navigate to AI Governance to inspect live agent latency, tool calls, and pause individual agents.

### Persona 3: Standard Employee (`employee@enterprise.demo` / `Password123!@#Secure`)
1. **Self-Service Portal**: View personal leave balances, shift attendance records, and downloadable payslips.
2. **Employee AI Assistant**: Ask *"How many annual leave days do I have left?"* $\to$ Scoped strictly to employee's own record.
