# Program 22: Security Hardening, Multi-Tenancy & Threat Defenses

## 1. Multi-Tenant Hard Partitioning
- Every database query enforces `organization_id == principal.tenant_id`.
- Tenant mismatch between JWT token and HTTP header `X-Tenant-ID` is rejected with `403 Forbidden`.

---

## 2. Adversarial AI Threat Matrix

| Threat Vector | Defense Mechanism | Test Evidence |
|---|---|---|
| **Direct Prompt Injection** | Multi-Layer Prompt Firewall | `tests/test_program_22_security.py` |
| **Indirect Document Injection** | Content Trust Scanner at RAG ingestion | Ingestion test suites |
| **Cross-Tenant Leakage** | TenantContext filter & object storage sandboxing | `tests/test_program_22_tenant_isolation.py` |
| **Unauthorized Consequential Mutation** | CommandBus + HITL Gating | `tests/test_program_22_hitl.py` |
