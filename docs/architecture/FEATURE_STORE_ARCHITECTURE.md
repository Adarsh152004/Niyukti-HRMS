# Feature Store Architecture

## 1. Declarative Feature Registry

The Feature Store maintains declarative definitions for all HR intelligence features, specifying:
- Datatype (`NUMERIC`, `CATEGORICAL`, `BOOLEAN`, `VECTOR`)
- Transformation logic (e.g. `months_between(current_date, joining_date)`)
- Sensitivity tier (`INTERNAL`, `SENSITIVE`, `PROTECTED_ATTRIBUTE`, `RESTRICTED`)
- Freshness SLA requirements
- Min/Max range constraints

---

## 2. Dual Serving Architecture

- **Offline Feature Store**: Generates versioned, point-in-time correct training datasets with deterministic splits (`TEMPORAL`, `ENTITY_GROUPED`, `RANDOM`).
- **Online Feature Store**: In-memory low-latency feature vector lookup per entity (e.g. `employee_id`) for real-time model inference.
