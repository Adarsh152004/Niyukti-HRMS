# Model Governance & Responsible AI

## 1. Lifecycle Release Stages

Every machine learning model version progresses through strictly audited stages:

```
DEVELOPMENT → EVALUATION → SHADOW → CANARY (5% - 50%) → ACTIVE → RESTRICTED / RETIRED / ROLLED_BACK
```

1. **`SHADOW`**: Receives production inference requests in parallel with the active model. Generates predictions for evaluation comparison but is **strictly prevented from mutating production HR data**.
2. **`CANARY`**: Receives a bounded percentage of production traffic (e.g. 10%, 25%, 50%). Automatically monitored for error spikes and drift.
3. **`ACTIVE`**: The primary authoritative production version.
4. **`ROLLED_BACK`**: Preserves full historical auditability while instantly reverting production traffic to the verified `rollback_target_version_id`.

---

## 2. Fairness & Deployment Gates

Before any model version can be activated into production, it must satisfy multi-criteria governance gates:

```
┌───────────────────────────────────────────────────────────┐
│                 ML DEPLOYMENT GATE CRITERIA               │
├───────────────────────────────────────────────────────────┤
│ 1. Performance Gate: Accuracy / F1 / MAE >= SLA           │
│ 2. Calibration Gate: Expected Calibration Error <= 0.20   │
│ 3. Fairness Gate: Demographic Parity Gap <= 0.15          │
│ 4. Security Gate: Sensitive training data PII compliance  │
└───────────────────────────────────────────────────────────┘
```

If any criterion fails, activation is automatically blocked.
