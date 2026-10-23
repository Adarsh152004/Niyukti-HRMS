# Program 20: End-to-End Runtime Execution Flows

## 1. Flow A: Read-Only Executive Strategic Query

```text
1. CEO asks in AI Chat: "Show me department-level attendance trends and high-risk attrition areas."
2. API Gateway:
   - Validates JWT token and extracts Actor (CEO) and Tenant (org-apex-01).
   - Verifies roles: {'SUPER_ADMIN', 'CEO'}.
3. Orchestrator instantiates Executive Strategy Agent (`ag-01`).
4. Reasoning Engine:
   - Queries Memory (Organization tier).
   - Queries RAG Knowledge Store for retention policies.
   - Deconstructs task into sub-goals:
     a. Query department attendance summary.
     b. Invoke predictive attrition ML model.
5. Governed MCP Server:
   - Executes `attendance.summary` tool (Risk: LOW, Capability: ATTENDANCE_READ).
   - Executes `ml.predict_attrition` tool (Risk: LOW, Capability: ANALYTICS_READ).
6. Response Generator:
   - Compiles structured Markdown response with interactive chart metadata.
   - Appends verifiable citations (`POL-BEN-LV-01 v3.2`).
7. Result streamed to CEO Dashboard via WebSocket / HTTP JSON.
```

---

## 2. Flow B: High-Risk Employee Termination Mutation

```text
1. HR Admin submits: "Terminate employee EMP-1004 due to gross misconduct."
2. API Gateway validates actor and resolves HR Manager Agent (`ag-02`).
3. Agent evaluates request and proposes `employee.terminate(employee_id='EMP-1004')`.
4. Governed MCP Tool Server:
   - Detects tool `employee.terminate` carries Risk Level CRITICAL.
   - Halts autonomous execution immediately.
   - Creates `ApprovalRequest` (Status: PENDING) with diff, reason, and policy citations.
   - Returns HITL challenge to user: "Action requires Human Approver Sign-Off".
5. Human Approver (CEO / Super Admin) opens `/approvals` UI:
   - Inspects affected employee profile, severance impacts, and evidence.
   - Clicks [APPROVE].
6. Approval API dispatches `TerminateEmployeeCommand` to CQRS CommandBus.
7. CommandBus executes inside `PostgresUnitOfWork`:
   - Updates employee status to `TERMINATED`.
   - Stages `EmployeeTerminated` event in Transactional Outbox.
   - Commits database transaction atomically.
8. EventBus processes Outbox:
   - Appends record to immutable SHA-256 audit ledger.
   - Enqueues notification email to HR Operations.
   - Broadcasts real-time WebSocket event updating the Employee Directory UI.
```
