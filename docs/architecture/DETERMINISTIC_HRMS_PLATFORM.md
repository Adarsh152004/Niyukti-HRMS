# Deterministic Core HRMS Business Platform: Program 7

## 1. Executive Summary & Core Architectural Invariant

Program 7 provides the full operational implementation of the 15 core HRMS business domains with strict tenant boundaries, declarative repositories, application services, REST API endpoints, and Alembic database migrations.

### Offline & Resilience Guarantee:
$$\text{Deterministic HR Operations} \perp \text{LLM Availability}$$
All 15 modules are built to operate with 100% deterministic precision. If external LLM providers (OpenAI, Anthropic, Gemini, Groq, Mistral, etc.) are unreachable, degraded, or offline, core business capabilities (payroll calculation, employee check-in/out, leave accrual, performance goals, recruitment pipeline, policy publishing, approval workflows) remain **100% operational**.

---

## 2. The 15 Operational HRMS Modules

| # | Module | Core Entities | Application Service | REST Router |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Employee 360** | `Employee`, `EmployeeSkill`, `EmployeeDocument` | `Employee360Service` | `/api/v1/employees/{id}/360` |
| **2** | **Organization** | `Organization` | `OrganizationService` | `/api/v1/organizations` |
| **3** | **Department** | `Department` | `DepartmentService` | `/api/v1/departments` |
| **4** | **Designation** | `Designation` | `DesignationService` | `/api/v1/designations` |
| **5** | **Attendance** | `AttendanceRecord`, `Shift`, `Holiday` | `AttendanceService` | `/api/v1/attendance` |
| **6** | **Leave** | `LeaveRequest` | `LeaveService` | `/api/v1/leaves` |
| **7** | **Recruitment ATS**| `JobRequisition`, `Candidate`, `JobApplication`, `Interview` | `RecruitmentService` | `/api/v1/recruitment` |
| **8** | **Payroll** | `SalaryComponent`, `PayrollStatus` | `PayrollService` | `/api/v1/payroll` |
| **9** | **Performance** | `ReviewCycle`, `Goal`, `PerformanceReview` | `PerformanceService` | `/api/v1/performance` |
| **10**| **Learning (LMS)** | `Course`, `CourseEnrollment`, `Certification` | `LearningService` | `/api/v1/learning` |
| **11**| **Documents** | `EmployeeDocument` | `EmployeeDocumentService` | `/api/v1/documents` |
| **12**| **HR Policies** | `HRPolicy` | `HRPolicyService` | `/api/v1/policies` |
| **13**| **Approvals** | `ApprovalRequest`, `ApprovalDecision` | `ApprovalInboxService` | `/api/v1/approvals` |
| **14**| **Notifications** | `Notification` | `NotificationService` | `/api/v1/notifications` |
| **15**| **Reports** | `HRReportDefinition`, `HRReportExecution` | `ReportingService` | `/api/v1/reports` |

---

## 3. Extended External LLM & AI Adapters

First-class provider adapters available via `backend/ai/gateway/providers.py` and `backend/integrations/`:
- **Groq**: Ultra-low latency LPU inference adapter.
- **Mistral**: Mistral Large and Codestral models.
- **HuggingFace**: Serverless inference and dedicated endpoint adapter.
- **OpenRouter**: Meta-routing across global LLM models.
- **Cohere**: High-performance embedding and reranking.
- **Tavily Search**: Real-time web search and grounding context.
- **Supabase Storage**: Object storage bucket uploads and downloads.
