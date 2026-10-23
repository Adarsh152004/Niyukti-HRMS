# Security & Identity Architecture — AI-Powered Intelligent HRMS

## 1. Overview
The security architecture provides a unified identity, authentication, and capability-based authorization foundation. It supports human users, autonomous AI agents, background system processes, and external integrations while maintaining strict tenant isolation boundaries.

```
Authentication ("WHO are you?")
    ↓
JWT / Session / API Key / Agent Identity
    ↓
Actor Mapping (HUMAN, AI_AGENT, SYSTEM, EXTERNAL_INTEGRATION)
    ↓
TenantContext ("WHICH organization?")
    ↓
Authorization ("WHAT are you allowed to do?")
    ↓
RBAC + Capability Engine + HITL Governance
```

---

## 2. Actor Classification & Identity Integration
All security principals are mapped to the canonical `Actor` abstraction:

| Principal Type | ActorType | Credentials / Auth Mechanism | Capabilities & Roles |
| :--- | :--- | :--- | :--- |
| **Human User** | `HUMAN` | Email/Password, JWT Access/Refresh tokens | Assigned HRMS Roles (`SUPER_ADMIN`, `CEO`, `EMPLOYEE`, etc.) |
| **AI Agent** | `AI_AGENT` | Independent Agent Registration & Key | Explicit Capability Grants (e.g. `employee.read`) |
| **System Process** | `SYSTEM` | Internal Kernel / Service Tokens | Internal operational capabilities |
| **API Integration** | `EXTERNAL_INTEGRATION` | SHA-256 Hashed API Keys (`hrms_live_...`) | Explicit Scopes |

---

## 3. JWT & Refresh Token Lifecycle

### Access Tokens
- **Algorithm**: Configurable asymmetric/symmetric (default: `HS256`, abstract engine supports `RS256`/`ES256`).
- **Claims**: `sub`, `actor_id`, `organization_id`, `actor_type`, `roles`, `permissions`, `capabilities`, `jti`, `iat`, `exp`, `iss`, `aud`.
- **Validation**: Strict signature verification, expiration check, issuer/audience validation, and tenant binding matching.

### Refresh Tokens & Reuse Detection
- **Hashed Storage**: Raw refresh tokens are NEVER stored in the database. Only SHA-256 hashes are persisted.
- **Token Family Rotation**: Every token refresh issues a new refresh token in the same `family_id`.
- **Reuse Attack Mitigation**: If an already-used refresh token is presented (replay attack), the ENTIRE token family is immediately revoked, all active user sessions are terminated, and a `REFRESH_TOKEN_REUSE` security audit event is logged.

---

## 4. AI Agent Security & Anti-Impersonation
- AI Agents possess **explicit capabilities** (`capabilities: set[str]`).
- AI Agents MUST NOT impersonate human JWTs or acquire ungranted human/admin permissions.
- Agent lifecycle statuses (`REGISTERED`, `ACTIVE`, `SUSPENDED`, `REVOKED`, `DECOMMISSIONED`) enforce runtime authentication blocks upon suspension.

---

## 5. Security Audit Logging
Security-critical operations publish structured `SecurityEvent` audit records:
- Events: `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `TOKEN_REFRESH`, `REFRESH_TOKEN_REUSE`, `ACCOUNT_LOCKED`, `UNAUTHORIZED_ACTION`, `CROSS_TENANT_ACCESS_ATTEMPT`.
- Secret Masking Invariant: Passwords, raw JWTs, refresh tokens, and secret API keys are strictly excluded from all audit event payloads and log files.

---

## 6. Threat Model & Mitigation Summary
- **Password Attacks**: Bcrypt hashing (`passlib`), configurable password policy, 5-attempt lockout (15 min cooldown).
- **Session Hijacking**: Short-lived JWT access tokens (60 min) + session tracking with `logout_all_sessions`.
- **Replay Attacks**: Single-use refresh token rotation with token family revocation.
- **Cross-Tenant Escalation**: Strict header & token tenant matching (`JWT organization_id == TenantContext organization_id`).
