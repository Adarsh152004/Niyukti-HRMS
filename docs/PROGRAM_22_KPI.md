# Program 22: Dynamic KPI Engine & Data Provenance

## 1. Zero Hardcoded Dashboard Values
All metrics are computed in real time from domain aggregate repositories:

| Metric Name | Formula / Aggregation Method | Data Provenance Source |
|---|---|---|
| **Total Headcount** | $\sum \text{Active Employees}$ across departments | `PostgresEmployeeRepository` |
| **Attendance Rate** | $\frac{\text{Present Days}}{\text{Scheduled Work Days}} \times 100$ | `PostgresAttendanceRepository` |
| **Monthly Spend** | $\sum (\text{Base Salary} + \text{Allowances} - \text{Deductions})$ | `PostgresPayrollRepository` |
| **Voluntary Attrition** | $\frac{\text{Resignations (Trailing 12m)}}{\text{Average Headcount}} \times 100$ | `PostgresEmployeeRepository` |
| **Offer Acceptance Rate** | $\frac{\text{Accepted Offers}}{\text{Total Extended Offers}} \times 100$ | `PostgresRecruitmentRepository` |
