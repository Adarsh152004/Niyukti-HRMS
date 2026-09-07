# Program 17: AI Agent Runtime & Model Architecture

## 1. Agent Execution Lifecycle

```text
[TASK_RECEIVED]
      │
      ▼
[PLANNING & REASONING] (Multi-Provider LLM Router)
      │
      ▼
[CONTEXT BUDGETING] (System + Memory + Citations + Tools <= 8192 Tokens)
      │
      ▼
[TOOL PROPOSAL] (Structured Pydantic ReasoningDecision)
      │
      ▼
[CAPABILITY CHECK] (Agent allowed tool check)
      │
      ├──────────────────────────────┐
      │ LOW Risk                     │ HIGH Risk
      ▼                              ▼
[GOVERNED TOOL EXECUTION]    [HITL APPROVAL GATE]
      │                              │
      ▼                              ▼
[COMMAND BUS & UOW]          [PENDING HUMAN DECISION]
      │                              │
      ▼                              ▼
[OBSERVATION & RESPONSE]     [APPROVED -> DISPATCH COMMAND]
```

---

## 2. 24 Specialized HR Agents Catalog

| Agent ID | Role | Focus Area | Autonomy Level |
|---|---|---|---|
| `ag-01` | Executive Operations Agent | Strategic workforce KPIs & board analysis | L2 (Collaborative) |
| `ag-02` | Talent Acquisition Agent | Sourcing, candidate outreach, recruiter workflows | L2 (Collaborative) |
| `ag-03` | Resume Screening Agent | AI skill competency matching, parsing | L3 (Autonomous) |
| `ag-04` | Payroll Assistant Agent | Batch calculations, payslips, deductions | L1 (Supervised) |
| `ag-05` | Performance Agent | OKR calibration, 360 review synthesis | L2 (Collaborative) |
| `ag-06` | Attrition Predictor Agent | Machine learning retention risk scoring | L3 (Autonomous) |
| `ag-07` | Compliance & Audit Agent | SOC2, GDPR, policy violation detection | L3 (Autonomous) |
| `ag-08` | Employee Assistant Agent | Self-service HR queries, leave balance | L3 (Autonomous) |
| `ag-09` | Attendance Anomaly Agent | Biometric shift discrepancy alerts | L3 (Autonomous) |
| `ag-10` | Leave Policy Agent | Absence policy interpretation & RAG | L3 (Autonomous) |
| `ag-11` | Compensation Agent | Market salary benchmarks & equity | L1 (Supervised) |
| `ag-12` | Onboarding Agent | New hire task orchestration & checklists | L2 (Collaborative) |

---

## 3. Multi-Agent Delegation & Supervisor Hierarchy

- **Recruitment Supervisor (`ag-rec-sup`)** delegates to:
  - `ResumeScreeningAgent` $\to$ `CandidateRankingAgent` $\to$ `InterviewCoordinationAgent`
- **Delegation Safety Rules**:
  1. Capability Intersection (Child agent cannot exceed parent's assigned scope).
  2. Bounded Recursion Depth (Max depth = 3).
  3. Token & Cost Budget Inheritance.
  4. Collusion Detection & Independent Audit Trails.
