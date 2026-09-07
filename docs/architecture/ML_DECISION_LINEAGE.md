# Decision Lineage & Provenance Architecture

## 1. Cryptographic Provenance Chain

Every ML inference generates an immutable `PredictionLineage` record linking runtime outputs back to root data sources, feature versions, and policies:

```
PREDICTION [pred-xyz]
   ├── Model Version [v2]
   ├── Feature Set Version [1.0]
   ├── Dataset Version [dsv-101 (SHA-256 Checksum)]
   ├── Preprocessing Version [1.0]
   ├── Threshold Policy [v1 (Decision: 0.50, Abstain: 0.60)]
   ├── Input Feature Hashes (Hashed to preserve privacy)
   ├── Governance Policy Version [1.0]
   ├── Correlation ID [corr-abc]
   └── Real-World Outcome Feedback (Post-hoc evaluation)
```

---

## 2. Privacy & Data Minimization

To prevent unnecessary replication of sensitive employee data:
- Raw PII is scrubbed before dataset creation.
- Lineage records store SHA-256 hashes of feature values (`input_feature_hashes`) rather than copying raw confidential attributes into audit tables.
- Lineage records are append-only and cannot be mutated or deleted by AI agents.
