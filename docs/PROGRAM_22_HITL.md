# Program 22: Human-in-the-Loop (HITL) Command Center & Approvals

## 1. Consequential Action Policy
The following operations strictly mandate Human-in-the-Loop approval:
1. **Employment Termination**: (`employee.terminate`) $\to$ CRITICAL Risk.
2. **Compensation Adjustment**: (`payroll.update_salary`) $\to$ HIGH Risk.
3. **Monthly Payroll Run Commitment**: (`payroll.finalize`) $\to$ CRITICAL Risk.
4. **Bulk Employee Record Update**: (`employee.bulk_update`) $\to$ HIGH Risk.
5. **Security Clearance & Role Assignment**: (`security.assign_role`) $\to$ CRITICAL Risk.

---

## 2. Cryptographic Approval Lifecycle
- **Approval ID**: Cryptographically unique string (e.g. `appr-2201-org-apex-01`).
- **Signature Token**: SHA-256 digest binding `request_id`, `approver_id`, and `proposed_mutation_hash`.
- **Command Injection**: When approved, signature token is injected into the CQRS `Command` payload and recorded in the append-only audit ledger.
