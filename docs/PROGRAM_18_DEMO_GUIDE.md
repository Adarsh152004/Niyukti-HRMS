# Program 18: Interactive Demo Guide & Persona Walkthroughs

This guide provides step-by-step instructions for demonstrating the integrated AI-native HRMS across key enterprise personas.

---

## 1. Persona 1: CEO / Executive Strategy
1. Open the Web App at [http://localhost:5174/](http://localhost:5174/).
2. Login as Executive: `ceo@enterprise.demo` / `Password123!@#Secure`.
3. Open **CEO Command Center** (`/command`) or **AI Workspace** (`/ai`).
4. Ask: `"Give me a summary of total headcount, attendance rate, and attrition risk."`
5. **Verify**:
   - AI queries `analytics.kpi` and returns 128 employees, 94.6% attendance, 4.2% attrition risk.
   - Recommends an interactive workforce bar chart.
   - Highlights Engineering and Sales department trends with verifiable source links.

---

## 2. Persona 2: Employee Self-Service
1. Login as Employee: `employee@enterprise.demo` / `Password123!@#Secure`.
2. Open **AI Workspace Chat** (`/ai`).
3. Ask: `"How many days of annual leave do I have remaining?"`
4. **Verify**:
   - AI resolves employee context and retrieves deterministic leave balance (14 days remaining).
5. Ask: `"What is the company policy on parental and maternity leave?"`
6. **Verify**:
   - Returns 26 weeks paid leave entitlement with explicit citation: `Policy POL-BEN-LV-01 (Page 4)`.

---

## 3. Persona 3: HR Admin & Governed HITL Mutation
1. Login as HR Admin: `admin@enterprise.demo` / `Password123!@#Secure`.
2. In the AI Command Center, type: `"Increase base compensation for Rahul Verma to $145,000."`
3. **Verify**:
   - AI recognizes `HIGH` risk mutation on compensation.
   - Direct execution is halted $\to$ generates `ApprovalRequest` (`hitl-sal-01`).
4. Navigate to **HITL Approval Center** (`/approvals`).
5. **Verify**:
   - Review pending compensation adjustment with risk score and affected employee record.
   - Click **Approve**.
   - The transaction is executed via CommandBus and recorded in the tamper-evident audit ledger.

---

## 4. Persona 4: Recruiter Sourcing & Interview Scheduling
1. Navigate to **Recruitment Pipeline** (`/recruitment`).
2. Review candidate applications for *Senior Fullstack Engineer*.
3. Click **Screen & Rank Candidates** (triggers `ResumeScreeningAgent` and `CandidateRankingAgent`).
4. Advance the top candidate to *Technical Interview*.
5. **Verify**:
   - Calendar event is scheduled with auto-generated meeting link (`https://meet.enterprise.demo/...`).
   - Candidate receives automated interview invitation notification.

---

## 5. Persona 5: AI Operator & Governance Center
1. Navigate to **AI Governance & Safety** (`/governance`).
2. Review live AI fleet health, token consumption ($1.44 estimated cost today), and prompt firewall metrics.
3. Test **Emergency Kill-Switch**: Click **Pause All AI Agents**.
4. **Verify**:
   - Status updates to `PAUSED`.
   - Security audit event is logged.
   - Click **Resume AI Agents** to restore normal autonomous operations.
