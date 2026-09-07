# Program 20: AI Runtime & Agent Fleet Specification

## 1. 24 Specialized Agents Fleet & Autonomy Modes

| Agent ID | System Role | Display Name | Autonomy Mode | Max Tools / Task | Max Delegation Depth |
|---|---|---|---|---|---|
| `ag-01` | `EXECUTIVE_STRATEGY` | Executive Strategy Agent | Collaborative (L2) | 10 | 3 |
| `ag-02` | `HR_MANAGER` | HR Manager Agent | Collaborative (L2) | 12 | 2 |
| `ag-03` | `RECRUITMENT_SUPERVISOR` | Recruitment Supervisor Agent | Collaborative (L2) | 15 | 2 |
| `ag-04` | `RESUME_SCREENING` | Resume Screening Agent | Autonomous (L3) | 5 | 0 |
| `ag-05` | `CANDIDATE_RANKING` | Candidate Ranking Agent | Autonomous (L3) | 5 | 0 |
| `ag-06` | `INTERVIEW_COORDINATION`| Interview Coordination Agent | Autonomous (L3) | 8 | 0 |
| `ag-07` | `EMPLOYEE_ASSISTANT` | Employee Assistant Agent | Autonomous (L3) | 6 | 0 |
| `ag-08` | `ONBOARDING` | Onboarding Agent | Collaborative (L2) | 10 | 1 |
| `ag-09` | `OFFBOARDING` | Offboarding Agent | Collaborative (L2) | 10 | 1 |
| `ag-10` | `ATTENDANCE_ANOMALY` | Attendance Anomaly Agent | Autonomous (L3) | 8 | 0 |
| `ag-11` | `LEAVE_POLICY` | Leave Policy Agent | Autonomous (L3) | 6 | 0 |
| `ag-12` | `PAYROLL_ASSISTANT` | Payroll Assistant Agent | Supervised (L1) | 8 | 0 |
| `ag-13` | `PERFORMANCE` | Performance Agent | Collaborative (L2) | 10 | 1 |
| `ag-14` | `SKILL_GAP` | Skill Gap Agent | Autonomous (L3) | 6 | 0 |
| `ag-15` | `LEARNING` | Learning Agent | Autonomous (L3) | 6 | 0 |
| `ag-16` | `CAREER_COACH` | Career Coach Agent | Collaborative (L2) | 8 | 0 |
| `ag-17` | `ATTRITION_PREDICTOR`| Attrition Predictor Agent | Autonomous (L3) | 5 | 0 |
| `ag-18` | `RETENTION_INTERVENTION`| Retention Intervention Agent| Supervised (L1) | 8 | 0 |
| `ag-19` | `SENTIMENT_PULSE` | Sentiment & Pulse Agent | Autonomous (L3) | 5 | 0 |
| `ag-20` | `WORKFORCE_PLANNING` | Workforce Planning Agent | Collaborative (L2) | 10 | 1 |
| `ag-21` | `HR_ANALYTICS` | HR Analytics Agent | Autonomous (L3) | 8 | 0 |
| `ag-22` | `COMPLIANCE_AUDIT` | Compliance & Audit Agent | Autonomous (L3) | 10 | 0 |
| `ag-23` | `DOCUMENT_INTELLIGENCE`| Document Intelligence Agent | Autonomous (L3) | 8 | 0 |
| `ag-24` | `NOTIFICATION` | Notification Agent | Autonomous (L3) | 5 | 0 |

---

## 2. Multi-Provider AI Gateway
- **Primary Live Routing**: Google Gemini (`gemini-1.5-flash`) via `GEMINI_API_KEY`.
- **Secondary Live Routing**: Groq Llama-3 (`llama-3.3-70b-versatile`) via `GROQ_API_KEY`.
- **Additional Live Adapters**: Mistral AI, OpenAI, Anthropic Claude.
- **Offline Fallback**: `MockLLMProvider` ensuring 100% deterministic test execution and zero-dependency local testing.
