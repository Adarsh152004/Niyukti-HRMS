# Program 22: End-to-End Golden Paths & Validation Scenarios

## 1. 10 End-to-End Real-World Golden Paths
1. **CEO Strategic Workforce Query**: CEO asks for workforce summary $\to$ AI Gateway resolves to `gemini` $\to$ KPI engine aggregates metrics $\to$ RAG retrieves policy with citations $\to$ response delivered.
2. **Recruitment ATS Workflow**: Recruiter posts job $\to$ candidate applied $\to$ resume analyzed $\to$ ranking scores computed $\to$ interview scheduled.
3. **Candidate Selection & Offer**: Candidate selected $\to$ offer package generated $\to$ approval challenge issued $\to$ notification dispatched.
4. **Employee Onboarding**: New employee onboarded $\to$ checklist assigned $\to$ document signed $\to$ buddy assigned.
5. **Employee Leave Request**: Employee submits 3-day leave $\to$ balance verified $\to$ policy checks passed $\to$ manager approved.
6. **High-Risk AI Compensation Mutation**: Agent proposes salary update $\to$ RiskEngine flags HIGH risk $\to$ halts for HITL $\to$ SuperAdmin signs off in UI $\to$ PostgreSQL commits $\to$ Outbox stages event.
7. **Monthly Payroll Run Commitment**: Payroll administrator verifies calculations $\to$ approval challenge completed $\to$ committed to ledger.
8. **Policy Document Ingestion & RAG**: Policy uploaded $\to$ sanitized $\to$ chunked $\to$ embedded in pgvector $\to$ verifiable citation served.
9. **Predictive Attrition Risk Intervention**: ML engine detects flight risk $\to$ advisory insight generated with decision lineage $\to$ no automatic penalty applied.
10. **Adversarial Tenant Attack Defense**: Tenant A attempts to read Tenant B employee record $\to$ rejected with 403 Forbidden $\to$ security audit logged.
