# Specialized AI HR Agent Catalog (24 Standard Agents)

## 1. Overview & Architectural Principles

The 24 Specialized AI HR Agents form the operational reasoning intelligence layer of the HRMS.
Every agent is a specialization of the enterprise **Agent Runtime** bound by:
- Explicit capability profiles (`Granted` and `Prohibited`)
- Deterministic tool policies (`ALLOW`, `DENY`, `REQUIRES_APPROVAL`)
- Pre-retrieval knowledge scoping
- Tiered memory isolation (`AGENT`, `TEAM`, `ORGANIZATION`, `EMPLOYEE`)
- Supervisor hierarchy links
- Strict non-negotiable invariant: $\text{AI Agent} \neq \text{Authority}$

---

## 2. Supervisor Hierarchy Structure

```
SYSTEM / GOVERNANCE
  │
  ├── EXECUTIVE_HR_AGENT
  │     ├── HR_MANAGER_AGENT
  │     │     ├── RECRUITMENT_AGENT
  │     │     │     ├── RESUME_SCREENING_AGENT
  │     │     │     ├── CANDIDATE_RANKING_AGENT
  │     │     │     └── INTERVIEW_INTELLIGENCE_AGENT
  │     │     │
  │     │     ├── EMPLOYEE_ASSISTANT_AGENT
  │     │     ├── ONBOARDING_AGENT
  │     │     ├── OFFBOARDING_AGENT
  │     │     ├── ATTENDANCE_AGENT
  │     │     ├── LEAVE_MANAGEMENT_AGENT
  │     │     ├── PAYROLL_ASSISTANT_AGENT
  │     │     ├── PERFORMANCE_AGENT
  │     │     ├── SKILL_GAP_AGENT
  │     │     ├── LEARNING_AGENT
  │     │     ├── CAREER_COACH_AGENT
  │     │     │
  │     │     ├── ATTRITION_AGENT
  │     │     │     └── RETENTION_AGENT
  │     │     │
  │     │     ├── SENTIMENT_AGENT
  │     │     └── NOTIFICATION_AGENT
  │     │
  │     ├── WORKFORCE_PLANNING_AGENT
  │     ├── HR_ANALYTICS_AGENT
  │     └── COMPLIANCE_AGENT
  │           └── DOCUMENT_INTELLIGENCE_AGENT
```

---

## 3. The 24 Specialized Agent Specifications

| No. | Role | Supervisor | Autonomy Mode | Routing Tier | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `EXECUTIVE_HR_AGENT` | System / Board | `SUPERVISED` | POWER | Executive intelligence, org-wide KPI summaries, workforce simulations. |
| 2 | `HR_MANAGER_AGENT` | `EXECUTIVE_HR_AGENT` | `SUPERVISED` | BALANCED | Daily HR operational coordination, workflow task queues, manager escalations. |
| 3 | `RECRUITMENT_AGENT` | `HR_MANAGER_AGENT` | `SUPERVISED` | BALANCED | Job requisitions, recruitment funnel monitoring, interview workflow. |
| 4 | `RESUME_SCREENING_AGENT` | `RECRUITMENT_AGENT` | `AUTONOMOUS_LOW_RISK` | FAST | Untrusted resume parsing, skill extraction, requirement matching. |
| 5 | `CANDIDATE_RANKING_AGENT` | `RECRUITMENT_AGENT` | `AUTONOMOUS_WITH_APPROVAL` | BALANCED | ML candidate scoring, explainable evidence generation, ABSTAIN support. |
| 6 | `INTERVIEW_INTELLIGENCE_AGENT` | `RECRUITMENT_AGENT` | `ASSISTED` | BALANCED | Structured interview question preparation, transcript synthesis. |
| 7 | `EMPLOYEE_ASSISTANT_AGENT` | `HR_MANAGER_AGENT` | `ASSISTED` | FAST | Self-service HR assistant strictly scoped to authenticated employee. |
| 8 | `ONBOARDING_AGENT` | `HR_MANAGER_AGENT` | `AUTONOMOUS_LOW_RISK` | BALANCED | New hire onboarding checklists, document verification workflows. |
| 9 | `OFFBOARDING_AGENT` | `HR_MANAGER_AGENT` | `SUPERVISED` | BALANCED | Exit workflows, IT asset return tracking, exit interview scheduling. |
| 10 | `ATTENDANCE_AGENT` | `HR_MANAGER_AGENT` | `AUTONOMOUS_LOW_RISK` | FAST | Deterministic attendance monitoring, anomaly alerts, regularizations. |
| 11 | `LEAVE_MANAGEMENT_AGENT` | `HR_MANAGER_AGENT` | `AUTONOMOUS_LOW_RISK` | FAST | Leave policy guidance, deterministic balance queries, conflict checks. |
| 12 | `PAYROLL_ASSISTANT_AGENT` | `HR_MANAGER_AGENT` | `SUPERVISED` | BALANCED | Payslip item explanations, variance detection (read-only, no mutations). |
| 13 | `PERFORMANCE_AGENT` | `HR_MANAGER_AGENT` | `ASSISTED` | BALANCED | Goal tracking, performance appraisal review synthesis, growth areas. |
| 14 | `SKILL_GAP_AGENT` | `HR_MANAGER_AGENT` | `AUTONOMOUS_LOW_RISK` | BALANCED | Department skill matrix analysis, competency deficiency detection. |
| 15 | `LEARNING_AGENT` | `HR_MANAGER_AGENT` | `AUTONOMOUS_LOW_RISK` | FAST | Course catalog recommendations, personalized training plans, compliance. |
| 16 | `CAREER_COACH_AGENT` | `HR_MANAGER_AGENT` | `ADVISORY` | BALANCED | Internal progression roadmaps, career development suggestions. |
| 17 | `ATTRITION_AGENT` | `HR_MANAGER_AGENT` | `SUPERVISED` | BALANCED | Consumes ML attrition risk, factor attribution, triggers retention plans. |
| 18 | `RETENTION_AGENT` | `ATTRITION_AGENT` | `SUPERVISED` | BALANCED | Tailored engagement plans, manager 1-on-1 guides, outcome tracking. |
| 19 | `SENTIMENT_AGENT` | `HR_MANAGER_AGENT` | `AUTONOMOUS_LOW_RISK` | FAST | Aggregate workplace pulse sentiment, anonymized culture health. |
| 20 | `WORKFORCE_PLANNING_AGENT` | `EXECUTIVE_HR_AGENT` | `SUPERVISED` | POWER | Headcount demand projections, capacity models, digital twin simulations. |
| 21 | `HR_ANALYTICS_AGENT` | `EXECUTIVE_HR_AGENT` | `AUTONOMOUS_LOW_RISK` | BALANCED | Natural language quantitative analytics, KPI visual dashboard generation. |
| 22 | `COMPLIANCE_AGENT` | `EXECUTIVE_HR_AGENT` | `SUPERVISED` | BALANCED | Labor law monitoring, certification expiry alerts, audit trail verification. |
| 23 | `DOCUMENT_INTELLIGENCE_AGENT` | `COMPLIANCE_AGENT` | `AUTONOMOUS_LOW_RISK` | FAST | DataFirewall document classification, metadata extraction, validation. |
| 24 | `NOTIFICATION_AGENT` | `HR_MANAGER_AGENT` | `AUTONOMOUS_LOW_RISK` | FAST | Governed multi-channel message dispatching and scheduled digests. |
