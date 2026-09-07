# Program 21: End-to-End Business Scenarios & Golden Paths

## 1. Automated Golden Path Scenarios
1. **Golden Path 1: CEO Strategic Query**: CEO asks for workforce summary $\to$ AI Gateway resolves to `gemini` $\to$ KPI engine aggregates metrics $\to$ RAG retrieves policy with citations $\to$ response delivered with chart metadata.
2. **Golden Path 2: HR Attrition Analysis**: HR asks for flight risk $\to$ ML engine generates calibrated prediction with lineage $\to$ no automatic employment decision is taken.
3. **Golden Path 3: Employee Leave Submission**: Employee requests 3 days leave $\to$ Leave Policy agent verifies balance $\to$ submits draft $\to$ dispatches `SubmitLeaveCommand` via CommandBus.
4. **Golden Path 4: Governed Employee Termination**: HR requests termination $\to$ Offboarding agent proposes `employee.terminate` $\to$ RiskEngine flags CRITICAL $\to$ halts for human approval $\to$ SuperAdmin approves in `/approvals` $\to$ PostgreSQL commits, Outbox stages event, email sent, SHA-256 audit updated.
5. **Golden Path 5: Monthly Payroll Commitment**: Payroll admin requests release $\to$ calculation preview generated $\to$ approval challenge issued $\to$ committed upon sign-off.
6. **Golden Path 6: Recruiter Candidate Ranking**: Recruiter asks to rank applicants $\to$ ATS scoring extracts skills $\to$ candidate match scores rendered.
7. **Golden Path 7: Authorized Policy Search**: Employee asks for parental leave details $\to$ RAG pre-retrieval role check passes $\to$ verifiable citation returned.
