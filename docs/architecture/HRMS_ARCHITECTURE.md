# AI-Powered Intelligent HRMS — Architecture

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [Architecture Overview](#2-architecture-overview)
3. [Layer Architecture](#3-layer-architecture)
4. [Enterprise Runtime](#4-enterprise-runtime)
5. [HRMS Core Domain](#5-hrms-core-domain)
6. [AI Intelligence Layer](#6-ai-intelligence-layer)
7. [Autonomous Agent Architecture](#7-autonomous-agent-architecture)
8. [Autonomy Level Framework](#8-autonomy-level-framework)
9. [Human-in-the-Loop (HITL)](#9-human-in-the-loop-hitl)
10. [Governance & Safety](#10-governance--safety)
11. [AI Decision Explainability](#11-ai-decision-explainability)
12. [Agent Performance Framework](#12-agent-performance-framework)
13. [Command Architecture](#13-command-architecture)
14. [Multi-Channel Architecture](#14-multi-channel-architecture)
15. [Security & RBAC](#15-security--rbac)
16. [PII Protection](#16-pii-protection)
17. [Database Architecture](#17-database-architecture)
18. [External Integrations](#18-external-integrations)
19. [WhatsApp Integration](#19-whatsapp-integration)
20. [CLI Architecture](#20-cli-architecture)
21. [Future Web Dashboard](#21-future-web-dashboard)
22. [Agent Ecosystem](#22-agent-ecosystem)
23. [Implementation Roadmap](#23-implementation-roadmap)

---

## 1. Product Vision

**AI-Powered Intelligent HRMS** is an enterprise-grade Human Resource Management System where traditional HRMS functionality is combined with autonomous AI agents, intelligent analytics, predictive capabilities, workflow automation, contextual assistance, governance, explainability, and human-in-the-loop control.

### This is NOT:
- A traditional HR CRUD application
- An LLM chatbot attached to a database
- A system where AI operates without governance

### This IS:
- An autonomous multi-agent HR organization
- A platform where human authority is always enforceable
- A system with full audit trails, explainability, and HITL gates
- An architecture where AI and humans collaborate under governance

---

## 2. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          USER GROUP                                       │
│         HR Admin │ Manager │ Employee │ CEO / Authorized Handler          │
└─────────────────────────────┬────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────────┐
│                        INTERFACE LAYER                                    │
│  Web Dashboard │ Mobile/Web App │ CLI │ Chat Interface │ WhatsApp         │
└─────────────────────────────┬────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────────┐
│                        SECURITY LAYER                                     │
│  JWT Auth │ RBAC │ Data Encryption │ Audit Logs │ Backup & Recovery       │
└─────────────────────────────┬────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────────┐
│                      HRMS CORE ENGINE                                     │
│  Auth │ Authorization │ Workflow │ Business Logic │ AI Coordination       │
│  Notifications │ Approval Workflow │ Audit                                 │
└──────────────┬──────────────────────────────────┬───────────────────────┘
               │                                  │
┌──────────────▼──────────────┐    ┌──────────────▼────────────────────────┐
│    HRMS DOMAIN MODULES       │    │        AI INTELLIGENCE LAYER          │
│                              │    │                                        │
│ • Employee Management        │    │ • Resume Screening & Parsing           │
│ • Attendance & Leave         │    │ • Candidate Ranking                    │
│ • Performance Management     │    │ • Performance Prediction               │
│ • Learning & Training        │    │ • Attrition Prediction                 │
│ • Recruitment Management     │    │ • HR Assistant (Contextual Queries)    │
│ • Payroll Management         │    │ • Sentiment Analysis                   │
│ • Analytics Dashboard        │    │ • Survey Analysis                      │
│ • HR Policies                │    │ • Skill Gap Analysis                   │
└──────────────┬───────────────┘    └──────────────┬────────────────────────┘
               │                                  │
┌──────────────▼──────────────────────────────────▼───────────────────────┐
│                          DATABASE LAYER                                   │
│  PostgreSQL (Primary) │ Redis (Cache/Events) │ Qdrant (Vector Memory)    │
└──────────────────────────────────────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────────────────────┐
│                     EXTERNAL INTEGRATIONS                                 │
│  Email │ SMS │ Calendar │ Biometric Devices │ Cloud Storage │ Payment GW  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer Architecture

### Interface Layer
All channels connect to the same command/application layer. No business logic lives in channel adapters.

| Channel | Actor | Status |
|---|---|---|
| Web Dashboard | All roles | Node 7 |
| Mobile/Web App | All roles | Node 7 |
| CLI (`asi-hr`) | CEO, HR Admin | Node 4 |
| Chat Interface | All roles | Node 5 |
| WhatsApp | CEO, authorized handlers | Node 8 |
| REST API | External systems | Node 4 |
| Autonomous Agents | AI agents | Node 5 |

### Security Layer
- **JWT Authentication** — Stateless token-based authentication
- **RBAC** — 8 role types with explicit permission grants
- **PII Protection** — Classification, masking, encryption
- **Audit Logs** — Immutable append-only audit trail
- **Backup & Recovery** — Planned in production deployment node

---

## 4. Enterprise Runtime

The `backend/runtime/` package provides the enterprise foundation:

| Component | Module | Responsibility |
|---|---|---|
| `EnterpriseKernel` | `kernel.py` | Singleton lifecycle controller |
| `ServiceRegistry` | `registry.py` | Named dependency container |
| `HRMSConfig` | `config.py` | Pydantic-settings typed configuration |
| `EventBus` | `events.py` | Pub/sub event bus (Redis-backed in production) |
| `KVStore` | `memory.py` | Key-value cache (Redis-backed in production) |
| `VectorStore` | `memory.py` | Semantic memory (Qdrant-backed in production) |
| `MiddlewareChain` | `middleware.py` | Composable async middleware pipeline |
| `TaskManager` | `task_manager.py` | Background task lifecycle management |
| Logging | `logging.py` | Structured JSON logging with PII masking |

---

## 5. HRMS Core Domain

35 domain entities organized into modules:

| Module | Entities |
|---|---|
| `organization` | Organization, Department, Designation |
| `employee` | Employee, EmployeeDocument, EmploymentHistory |
| `skills` | Skill, EmployeeSkill |
| `recruitment` | Job, JobApplication, Candidate, Interview |
| `attendance` | AttendanceRecord, Shift, Holiday |
| `leave` | LeaveRequest |
| `payroll` | PayrollRecord, SalaryComponent, Bonus, Deduction |
| `performance` | PerformanceGoal, KPI, PerformanceReview |
| `learning` | TrainingProgram, TrainingEnrollment, Certification, CareerPlan |
| `feedback` | Survey, Feedback, EmployeeSentiment |
| `policy` | HRPolicy |
| `notifications` | Notification |

---

## 6. AI Intelligence Layer

### Capabilities
- **Resume Screening** — Parse, extract skills, score against job requirements
- **Candidate Ranking** — AI-ranked shortlists with explainable evidence
- **Performance Prediction** — Forecast review ratings using KPIs and behavior signals
- **Attrition Prediction** — Predict attrition risk per employee
- **Sentiment Analysis** — Analyze survey responses and feedback
- **HR Assistant** — Contextual Q&A for employees and HR managers
- **Skill Gap Analysis** — Gap between current skills and target role requirements
- **Payroll Anomaly Detection** — Flag unusual payroll patterns

### Provider Abstraction
The `AIProvider` interface (`backend/ai/provider.py`) decouples all AI calls from specific vendors.
Concrete implementations: OpenAI, Google Gemini, Anthropic, or local models.

---

## 7. Autonomous Agent Architecture

### 24 Planned Agents

```
Strategic
├── CEO/HR Executive Agent
└── HR Manager Agent

Recruitment
├── Recruitment Agent
├── Resume Screening Agent
├── Candidate Ranking Agent
└── Interview Coordination Agent

Employee
├── Employee Management Agent
├── Attendance Agent
└── Leave Management Agent

Compensation
└── Payroll Agent

Performance
├── Performance Management Agent
└── Skill Gap Analysis Agent

Development
├── Learning & Training Agent
└── Career Development Agent

Retention
├── Attrition Prediction Agent
├── Employee Retention Agent
└── Sentiment Analysis Agent

Analytics
└── HR Analytics Agent

Compliance
├── HR Policy Agent
├── Compliance/Governance Agent
└── Audit Agent

Planning
└── Workforce Planning Agent

Support
├── Notification Agent
└── Employee HR Assistant
```

### Agent Communication
Agents communicate through the `EventBus` — never directly with each other or external systems.
All inter-agent coordination flows through the enterprise runtime.

---

## 8. Autonomy Level Framework

| Level | Name | Description | Approval Required |
|---|---|---|---|
| 0 | Human Only | Agent provides no recommendations | Always |
| 1 | AI Recommends | AI advises, human decides | Always |
| 2 | AI Prepares, Human Approves | AI prepares, human approves each action | Yes, per action |
| 3 | AI Executes Low-Risk | Low-risk reversible actions run autonomously | No, for LOW risk |
| 4 | AI Executes Approved Classes | Approved action categories run autonomously | Monitored |
| 5 | Fully Autonomous | Full autonomy within governance bounds | Monitored |

**Autonomy is configurable per**: agent, action, department, workflow, organization, risk level.

---

## 9. Human-in-the-Loop (HITL)

### States
```
PENDING → APPROVED ✓ (agent proceeds)
PENDING → REJECTED ✗ (agent aborts)
PENDING → ESCALATED → (higher authority reviews)
PENDING → EXPIRED → (escalate or cancel)
PENDING → CANCELLED (withdrawn)
```

### Required Fields
- `action_type`, `action_description`
- `requesting_agent_id`, `requesting_agent_role`
- `risk_level`, `priority`
- `resource_type`, `resource_id`
- `ai_recommendation`, `ai_confidence`, `ai_evidence`
- `required_reviewer_role`
- `escalation_target_role`
- `expires_at`

### Invariants
1. Agents **must never** silently execute governed actions
2. Human decisions **always** override AI recommendations
3. HITL records are **immutable** and permanently stored
4. HIGH-risk actions **always** require HITL before execution

---

## 10. Governance & Safety

### Safety Guardrail Chain
Evaluated for every autonomous action:
1. `EmergencyStopGuardrail` — Blocks all actions when emergency stop is active
2. `PolicyValidationGuardrail` — Validates against active HR policies
3. `RiskThresholdGuardrail` — Routes HIGH/CRITICAL risk to HITL
4. `ConfidenceThresholdGuardrail` — Requires approval for low-confidence AI actions
5. `PermissionValidationGuardrail` — Validates agent has required permissions
6. `RateLimitGuardrail` — Prevents action flooding

### Governance Policies
Configurable per: organization, department, agent role, action type.
More specific policies override broader ones.

### Example Autonomy Configuration
| Action | Autonomy Level | Approval Required |
|---|---|---|
| Resume Parsing | 5 | No |
| Candidate Ranking | 4 | No |
| Candidate Rejection | 2 | HR Manager |
| Interview Scheduling | 3 | No |
| Payroll Modification | 2 | HR Admin |
| Employee Termination | 2 | CEO/HR Admin |
| Policy Modification | 2 | CEO |

---

## 11. AI Decision Explainability

Every important AI decision produces an `AIDecision` record:

```python
AIDecision(
    decision_type=AIDecisionType.CANDIDATE_RANKING,
    decision="Candidate A ranked #1 of 12 applicants",
    confidence=0.91,
    evidence=[
        "5 years relevant experience",
        "87% required skill match",
        "required certification present",
    ],
    features_used=["experience_years", "skill_match_pct", "certification"],
    reasoning_summary="...",  # Concise — NOT raw chain-of-thought
    model_name="resume-ranking-v1",
    agent_role="CANDIDATE_RANKING_AGENT",
    risk_level=RiskLevel.LOW,
)
```

**Rules:**
- Private chain-of-thought is NEVER stored
- Evidence is human-readable and non-PII
- Human overrides are tracked with reason and reviewer ID
- Final outcome (after HITL) is linked back to the decision

---

## 12. Agent Performance Framework

Metrics tracked per agent per measurement period:

| Category | Metrics |
|---|---|
| Execution | task_success_rate, total_tasks, failed_tasks |
| Accuracy | accuracy, precision, recall, f1_score |
| Calibration | mean_confidence, confidence_calibration_error |
| Latency | avg_latency, p95_latency, p99_latency |
| Cost | total_cost, avg_cost_per_task |
| Human Oversight | human_override_rate, escalation_rate, recommendation_acceptance_rate |
| Safety | error_rate, policy_violation_rate, false_positive_rate, false_negative_rate |
| Outcome | outcome_quality_score |

Performance thresholds are **configurable per agent role** — no hardcoded "accuracy = good" assumptions.

---

## 13. Command Architecture

Every command (from any channel) flows through the same pipeline:

```
Channel Adapter
    ↓ [Transport only — no business logic]
Authentication
    ↓
Authorization (RBAC check)
    ↓
Command Parser
    ↓ [NL → Intent]
Intent
    ↓
Policy / Governance Check
    ↓
Agent / Workflow Selection
    ↓
Execution
    ↓
Validation
    ↓
HITL (if required)
    ↓
Result
    ↓
Audit Log
    ↓
Response Format (channel-specific)
```

### Command Model Fields
`command_id`, `actor_id`, `actor_role`, `channel`, `raw_input`, `intent`, `parameters`,
`risk_level`, `requires_approval`, `approval_request_id`, `hitl_request_id`,
`execution_status`, `assigned_agent_id`, `result`, `correlation_id`, `created_at`, `completed_at`

---

## 14. Multi-Channel Architecture

```
                    WEB
                    CLI
                    CHAT      ─────┐
                    WHATSAPP       │
                    API            ▼
                    AGENT    ───► Command Pipeline ──► Application Layer
```

**Rule**: All channels call the **same** application/command layer. Business logic is NEVER duplicated per channel.

---

## 15. Security & RBAC

### 8 Roles

| Role | Description | Can Approve |
|---|---|---|
| SUPER_ADMIN | Full platform access | CRITICAL |
| CEO | Strategic + command authority | CRITICAL |
| HR_ADMIN | Full HR module access | HIGH |
| HR_MANAGER | Day-to-day HR operations | MEDIUM |
| MANAGER | Department-level access | MEDIUM |
| EMPLOYEE | Own data only | — |
| AUDITOR | Read-only audit/reports | — |
| AI_AGENT | **Zero default permissions** — explicit scope only | — |

### AI_AGENT Invariant
`AI_AGENT` role has **zero default permissions**. Every agent must have an explicit `AgentPermissionScope` defining:
- `readable_resources`
- `writable_resources`
- `executable_actions`
- `forbidden_actions`
- `can_access_pii` (default: False)
- `max_autonomy_level`

---

## 16. PII Protection

### Classification Levels

| Level | Examples | Encrypt | Mask in Logs | AI Access |
|---|---|---|---|---|
| PUBLIC | Job title, department | No | No | Yes |
| INTERNAL | Employee ID, shift code | No | No | Yes |
| CONFIDENTIAL | Name, email, phone | No | Yes | No* |
| SENSITIVE | Salary, DOB, performance rating | Yes | Yes | No* |
| RESTRICTED | National ID, bank account, biometrics | Yes | Yes | No* |

*AI agents require explicit PII access grant in their `AgentPermissionScope`.

### Data Retention
Default 7-year retention post-offboarding for RESTRICTED fields (configurable per `PIIProtectionPolicy`).

---

## 17. Database Architecture

| Store | Technology | Purpose |
|---|---|---|
| Primary | PostgreSQL | All HRMS domain data |
| Cache | Redis | Sessions, rate limiting, counters |
| Events | Redis Pub/Sub | Inter-service events |
| Vector | Qdrant | Semantic search (resumes, policies) |

All database access goes through typed repository interfaces (implemented in Node 2).
No raw SQL in domain or application layer.

---

## 18. External Integrations

All external integrations use adapter interfaces (`backend/integrations/`):

| Integration | Interface | Status |
|---|---|---|
| Email | `EmailAdapter` | Interface only (Node 1) |
| Calendar | `CalendarAdapter` | Interface only (Node 1) |
| Cloud Storage | `StorageAdapter` | Interface only (Node 1) |
| WhatsApp | `WhatsAppAdapter` | Interface only (Node 1) |
| Biometric Devices | Planned | Future node |
| Payment Gateway | Planned | Future node |
| SMS | Planned | Future node |

---

## 19. WhatsApp Integration

The WhatsApp integration allows the CEO and authorized HR handlers to:
- Issue HRMS commands in natural language
- Receive alerts and reports
- Respond to HITL approval requests
- Trigger emergency stop
- Query agent status

**Architecture Rules:**
1. The `WhatsAppAdapter` handles only transport — no business logic
2. All commands received on WhatsApp are parsed and routed through the standard command pipeline
3. HITL decisions via WhatsApp are processed through the governance layer — not executed directly
4. Webhook signatures are always verified before processing

**Future implementation**: WhatsApp Business API (Meta) or Twilio WhatsApp.

---

## 20. CLI Architecture

Future CLI (`asi-hr`) will call the same application/command layer:

```bash
asi-hr employee list
asi-hr employee show <id>
asi-hr recruitment screen --job <id>
asi-hr analytics attrition
asi-hr agent status
asi-hr agent pause <role>
asi-hr approvals pending
asi-hr policy list
asi-hr audit recent --days 7
asi-hr autonomy status
asi-hr autonomy set --agent <role> --level 2
```

The CLI adapter translates commands into `Command` objects — no business logic in the CLI layer.

---

## 21. Future Web Dashboard

The web dashboard will provide:
- **HR Admin Dashboard** — Employee management, recruitment, payroll, compliance
- **Manager Dashboard** — Team attendance, leave approvals, performance reviews
- **Employee Portal** — Self-service for payslips, leave requests, training enrollment
- **CEO Dashboard** — Strategic analytics, AI recommendations, agent status
- **AI Control Panel** — Autonomy settings, HITL queue, agent performance metrics

Technology: React / TypeScript (Node 7).

---

## 22. Agent Ecosystem

### Communication Pattern
```
Agent A ──► EventBus ──► Agent B
              │
              └──► AuditLog
```

Agents never communicate directly. All coordination flows through the event bus.

### Agent Lifecycle
```
INACTIVE ──► ACTIVE ──► PAUSED ──► ACTIVE
                │
                └──► SUSPENDED (admin action required to restore)
                │
                └──► ERROR
```

### Governance Flow for Agent Actions
```
Agent wants to execute action
    │
    ▼
GuardrailChain.evaluate()
    │
    ├── EMERGENCY_STOP ──► Block immediately
    ├── BLOCK ──► Refuse action, log violation
    ├── REQUIRE_APPROVAL ──► Create HITLRequest, wait
    └── PASS ──► Execute action
                    │
                    └──► AuditEvent created
```

---

## 23. Implementation Roadmap

| Node | Scope | Key Deliverables |
|---|---|---|
| **Node 1** ✅ | Domain Transformation | Enterprise runtime, HRMS domain contracts, governance contracts, agent framework, command architecture, security, AI layer, 35 domain entities, 24 agent roster, 12 test files |
| Node 2 | Database Layer | PostgreSQL schemas, Alembic migrations, repository interfaces |
| Node 3 | Auth Service | JWT authentication, password hashing, token refresh, user management |
| Node 4 | Core HRMS API | Employee, Department, Leave, Attendance REST endpoints |
| Node 5 | Agent Framework | First 3 agents: Resume Screening, Attrition Prediction, HR Analytics |
| Node 6 | AI Layer | LLM integration, embedding pipeline, semantic search |
| Node 7 | Frontend | React/TypeScript dashboard |
| Node 8 | WhatsApp | WhatsApp Business API integration |
| Node 9 | Analytics | Advanced analytics, CEO query interface |
| Node 10 | Production | Docker, CI/CD, monitoring, deployment |
