# AI-Powered Intelligent HRMS — Predictive Machine Learning Platform & Decision Governance

## 1. Governance Principles for Predictive HR ML

1. **Decision Support Only**: ML predictions (attrition risk, performance forecasting, candidate qualification score) serve solely as analytical decision support. They **NEVER** constitute autonomous authority to execute adverse employment actions (e.g. terminations, demotions, rejection).
2. **Abstention & Uncertainty Handling**: If feature data is missing, anomalous, or out-of-distribution, the model explicitly emits `Decision.ABSTAIN` or `Decision.OUT_OF_DISTRIBUTION` rather than guessing.
3. **Immutable Decision Lineage**: Every prediction records complete lineage metadata:
   - Model name and semantic version.
   - Training dataset hash and date.
   - Feature vector snapshot.
   - Output probability and calibration metrics (ECE).
   - Calling actor, correlation ID, and timestamp.

---

## 2. Active Model Registry

| Model Name | Task | Target Output | Fallback Behavior on Low Confidence |
|---|---|---|---|
| `attrition_risk_v2` | Employee Flight Risk | Probability $[0.0, 1.0]$ | `ABSTAIN` + Notify HR Business Partner |
| `candidate_ranker_v1`| ATS Qualification Match | Score $[0, 100]$ + Explanations | Defer to Human Recruiter Manual Review |
| `performance_forecast_v1`| Quarterly OKR Trajectory| Performance Bracket | Defer to Manager Calibration Review |
| `attendance_anomaly_v3`| Biometric Anomaly Detection| Anomaly Flag + Confidence | Require Employee Timesheet Correction Review |
