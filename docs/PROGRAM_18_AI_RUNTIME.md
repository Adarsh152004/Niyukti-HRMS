# Program 18: Production AI Runtime & Model Operations

## 1. Unified Governed AI Path Invariant

```text
User / Event / Webhook
         │
         ▼
[AI Gateway / Multi-Provider Router] (OpenAI / Claude / Gemini / Offline Mock)
         │
         ▼
[Input & Prompt Firewalls] (PII Minimization + Prompt Injection Neutralization)
         │
         ▼
[Context Budgeting Engine] (Max 8,192 Tokens: System + Memory + RAG + Tools + User)
         │
         ▼
[Reasoning & Planning Engine] (Structured ReasoningDecision Pydantic Serialization)
         │
         ▼
[Governed MCP Server] (Capability Authorization Check against Agent Profile)
         │
         ▼
[Risk Engine Evaluation]
         │
    ┌────┴───────────────────────────┐
    │ LOW / MEDIUM Risk              │ HIGH / CRITICAL Risk (Salary, Terminations, Bulk Finalize)
    ▼                                ▼
[Direct CommandBus Dispatch]    [HITL Approval Gate]
    │                                │
    │                                ├─> Create ApprovalRequest Entity
    │                                ├─> Suspend Task Execution
    │                                └─> Await Human Decision in /approvals UI
    │                                          │ (Approved by Authorized Human)
    │                                          ▼
    └─────────────────────────────────> [Execute via CommandBus]
                                               │
                                               ▼
                                  [Transactional UnitOfWork]
                                  [PostgreSQL Persistence]
                                  [Outbox Event Staging]
                                  [EventBus Dispatch]
                                  [SHA-256 Tamper-Evident Audit Chain]
```

---

## 2. 24 Specialized Agents Runtime Matrix

| ID | Agent Name | Domain Focus | Autonomy Tier | Allowed Tool Namespace | Risk Policy | Memory Scope |
|---|---|---|---|---|---|---|
| `ag-01` | Executive Operations Agent | C-Suite workforce KPIs & Strategy | L2 (Collaborative) | `analytics.*`, `knowledge.search` | LOW | Organization |
| `ag-02` | HR Manager Agent | Departmental workflows & reviews | L2 (Collaborative) | `employee.*`, `leave.*`, `attendance.*` | MEDIUM | Department |
| `ag-03` | Recruitment Agent | Job postings & candidate pipelines | L2 (Collaborative) | `recruitment.*`, `candidate.*` | MEDIUM | Organization |
| `ag-04` | Resume Screening Agent | AI skill competency matching | L3 (Autonomous) | `candidate.screen`, `document.parse` | LOW | Task |
| `ag-05` | Candidate Ranking Agent | Objective rubric qualification scoring | L3 (Autonomous) | `candidate.rank`, `ml.predict` | LOW | Task |
| `ag-06` | Interview Coordination Agent | Calendar availability & meeting links | L3 (Autonomous) | `calendar.*`, `notification.*` | LOW | Task |
| `ag-07` | Employee Assistant Agent | Self-service Q&A & leave balance | L3 (Autonomous) | `employee.me`, `leave.balance`, `policy.*` | LOW | Employee |
| `ag-08` | Onboarding Agent | New hire task checklists & equipment | L2 (Collaborative) | `employee.onboard`, `document.request` | LOW | Employee |
| `ag-09` | Offboarding Agent | Exit clearances & asset return | L2 (Collaborative) | `employee.offboard`, `equipment.*` | HIGH (HITL) | Employee |
| `ag-10` | Attendance Anomaly Agent | Biometric shift discrepancy alerts | L3 (Autonomous) | `attendance.anomaly`, `attendance.get` | LOW | Department |
| `ag-11` | Leave Policy Agent | Absence policy interpretation & RAG | L3 (Autonomous) | `knowledge.search`, `leave.policy` | LOW | Organization |
| `ag-12` | Payroll Assistant Agent | Batch calculations & payslip summary | L1 (Supervised) | `payroll.preview`, `payroll.calculate` | HIGH (HITL) | Organization |
| `ag-13` | Performance Agent | OKR calibration & 360 review digest | L2 (Collaborative) | `performance.*`, `goals.*` | MEDIUM | Department |
| `ag-14` | Skill Gap Agent | Competency graph & training needs | L3 (Autonomous) | `skills.analyze`, `learning.*` | LOW | Department |
| `ag-15` | Learning Agent | Course recommendations & enrollments | L3 (Autonomous) | `learning.recommend`, `learning.assign` | LOW | Employee |
| `ag-16` | Career Coach Agent | Growth pathways & internal mobility | L2 (Collaborative) | `skills.*`, `jobs.list_internal` | LOW | Employee |
| `ag-17` | Attrition Predictor Agent | Machine learning retention risk scoring | L3 (Autonomous) | `ml.attrition_predict`, `analytics.*` | LOW | Department |
| `ag-18` | Retention Intervention Agent | Compensation benchmarks & surveys | L1 (Supervised) | `retention.propose`, `compensation.survey` | HIGH (HITL) | Department |
| `ag-19` | Sentiment & Pulse Agent | Anonymous pulse survey synthesis | L3 (Autonomous) | `pulse.aggregate`, `sentiment.analyze` | LOW | Organization |
| `ag-20` | Workforce Planning Agent | Headcount forecasting & capacity | L2 (Collaborative) | `workforce.forecast`, `budget.*` | MEDIUM | Organization |
| `ag-21` | HR Analytics Agent | Real-time SQL aggregations & charts | L3 (Autonomous) | `analytics.query_kpi` | LOW | Organization |
| `ag-22` | Compliance & Audit Agent | SOC2, GDPR, DSAR & policy checks | L3 (Autonomous) | `compliance.audit`, `audit.explore` | LOW | Organization |
| `ag-23` | Document Intelligence Agent | PDF/Docx OCR & metadata extraction | L3 (Autonomous) | `document.extract`, `knowledge.index` | LOW | Task |
| `ag-24` | Notification Agent | Multi-channel dispatch (Email/WA/Push)| L3 (Autonomous) | `email.send`, `whatsapp.send`, `push.send` | LOW | Task |

---

## 3. Multi-Agent Delegation Hierarchy

```text
                       [Executive Supervisor]
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
[Recruitment Supervisor]  [Workforce Supervisor]  [Compliance Supervisor]
         │                       │                       │
 ┌───────┼───────┐       ┌───────┼───────┐               ▼
 ▼       ▼       ▼       ▼       ▼       ▼       [Compliance Agent]
[Resume][Rank] [Coord] [Attrition][Perf] [Skill]
Agent   Agent  Agent   Agent      Agent  Agent
```

- **Delegation Rules**:
  1. Capability Intersection: Workers can only execute tools granted to both the Supervisor and Worker.
  2. Bounded Recursion: Maximum call depth $= 3$.
  3. Budget Inheritance: Child agents consume tokens and tool limits from the root task budget.
  4. Collusion Detection: Independent audit ledger records every supervisor $\to$ worker delegation event.
