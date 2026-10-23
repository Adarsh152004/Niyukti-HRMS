# AI-Powered Intelligent HRMS — Canonical 24-Agent Catalog

## Executive Summary
This document establishes the canonical specification for the 24 specialized AI HR agents comprising the autonomous agent fleet. Each agent operates under strict least-privilege boundaries and adheres to the non-negotiable invariant:

$$\mathbf{LLM \neq AUTHORITY}$$

---

## Agent Specification Table

| Agent ID | System Role Name | Autonomy Level | Allowed Tool Namespaces | Forbidden Actions | Risk Budget | Memory Scope | Delegation Depth | HITL Threshold |
|---|---|---|---|---|---|---|---|---|
| `ag-01` | Executive Strategy Agent | L2 (Collaborative) | `analytics.*`, `knowledge.search` | Direct employee record mutation | LOW | Organization | 3 (Supervisor) | Automatic on mutations |
| `ag-02` | HR Manager Agent | L2 (Collaborative) | `employee.*`, `leave.*`, `attendance.*` | Payroll release, Global policy edit | MEDIUM | Department | 2 (Supervisor) | > $5k salary change |
| `ag-03` | Recruitment Supervisor Agent | L2 (Collaborative) | `recruitment.*`, `candidate.*` | Autonomous job offer sign-off | MEDIUM | Organization | 2 (Supervisor) | Offer generation |
| `ag-04` | Resume Screening Agent | L3 (Autonomous) | `candidate.screen`, `document.parse` | Modifying candidate status | LOW | Task | 0 (Worker) | N/A |
| `ag-05` | Candidate Ranking Agent | L3 (Autonomous) | `candidate.rank`, `ml.predict` | Final hiring decision | LOW | Task | 0 (Worker) | N/A |
| `ag-06` | Interview Coordination Agent | L3 (Autonomous) | `calendar.*`, `notification.*` | Calendar deletion outside slot | LOW | Task | 0 (Worker) | N/A |
| `ag-07` | Employee Assistant Agent | L3 (Autonomous) | `employee.me`, `leave.balance`, `policy.*` | Accessing coworker data | LOW | Employee | 0 (Worker) | N/A |
| `ag-08` | Onboarding Agent | L2 (Collaborative) | `employee.onboard`, `document.request` | Skipping compliance steps | LOW | Employee | 1 | N/A |
| `ag-09` | Offboarding Agent | L2 (Collaborative) | `employee.offboard`, `equipment.*` | Autonomous termination commit | HIGH | Employee | 1 | All termination steps |
| `ag-10` | Attendance Anomaly Agent | L3 (Autonomous) | `attendance.anomaly`, `attendance.get` | Direct timesheet modification | LOW | Department | 0 (Worker) | Timesheet overrides |
| `ag-11` | Leave Policy Agent | L3 (Autonomous) | `knowledge.search`, `leave.policy` | Overriding leave accrual rules | LOW | Organization | 0 (Worker) | Policy exceptions |
| `ag-12` | Payroll Assistant Agent | L1 (Supervised) | `payroll.preview`, `payroll.calculate` | Unsupervised ledger commit | HIGH | Organization | 0 (Worker) | All batch commitments |
| `ag-13` | Performance Agent | L2 (Collaborative) | `performance.*`, `goals.*` | Setting final ratings | MEDIUM | Department | 1 | Calibration changes |
| `ag-14` | Skill Gap Agent | L3 (Autonomous) | `skills.analyze`, `learning.*` | Modifying mandatory certifications | LOW | Department | 0 (Worker) | N/A |
| `ag-15` | Learning Agent | L3 (Autonomous) | `learning.recommend`, `learning.assign`| Paid course purchase | LOW | Employee | 0 (Worker) | Budget approvals |
| `ag-16` | Career Coach Agent | L2 (Collaborative) | `skills.*`, `jobs.list_internal` | Direct promotion scheduling | LOW | Employee | 0 (Worker) | Promotion actions |
| `ag-17` | Attrition Predictor Agent | L3 (Autonomous) | `ml.attrition_predict`, `analytics.*` | Direct adverse actions | LOW | Department | 0 (Worker) | N/A |
| `ag-18` | Retention Intervention Agent | L1 (Supervised) | `retention.propose`, `compensation.survey`| Autonomous counter-offers | HIGH | Department | 0 (Worker) | All salary adjustments |
| `ag-19` | Sentiment & Pulse Agent | L3 (Autonomous) | `pulse.aggregate`, `sentiment.analyze`| De-anonymizing responses | LOW | Organization | 0 (Worker) | N/A |
| `ag-20` | Workforce Planning Agent | L2 (Collaborative) | `workforce.forecast`, `budget.*` | Headcount authorization | MEDIUM | Organization | 1 | Budget revisions |
| `ag-21` | HR Analytics Agent | L3 (Autonomous) | `analytics.query_kpi` | Raw SQL database access | LOW | Organization | 0 (Worker) | N/A |
| `ag-22` | Compliance & Audit Agent | L3 (Autonomous) | `compliance.audit`, `audit.explore` | Modifying audit trail hashes | LOW | Organization | 0 (Worker) | Non-compliance alerts |
| `ag-23` | Document Intelligence Agent | L3 (Autonomous) | `document.extract`, `knowledge.index` | Direct database schema changes | LOW | Task | 0 (Worker) | Low-confidence OCR |
| `ag-24` | Notification Agent | L3 (Autonomous) | `email.send`, `whatsapp.send`, `push.send` | Spoofing executive identities | LOW | Task | 0 (Worker) | Broadcasts > 100 users |
