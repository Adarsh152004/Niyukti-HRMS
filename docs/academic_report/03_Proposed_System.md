# CHAPTER 3: PROPOSED SYSTEM

## 3.1 OUTLINE OF PROPOSED WORK

The proposed system, **Niyukti**, introduces an agentic enterprise architecture that transforms passive HR database management into an autonomous, conversational, and governed multi-agent ecosystem. 

Unlike traditional software that relies on fixed navigational menus and static input forms, Niyukti enables executive leaders, HR managers, and employees to issue natural language commands (e.g., *"Recruit a Senior AI Engineer"*, *"Run monthly payroll batch"*, or *"Is Aditya present today?"*). The system analyzes the query, retrieves factual data from enterprise databases or policy vector stores, constructs structured artifacts (such as Job Descriptions or Payroll Statements in Indian Rupees `₹`), and routes high-risk tasks through a deterministic **Human-in-the-Loop (HITL)** approval gate before autonomous execution.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXECUTIVE USER INTERFACE                         │
│  📱 CEO Mobile Chat (Port 5174)   │   💻 Enterprise Workspace (Port 5185)│
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ (FastAPI SSE Stream)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH MULTI-AGENT FABRIC                         │
│  🧠 Router ──► 🎯 Recruitment ──► 💰 Payroll ──► 📊 Analyst ──► 📜 RAG  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ (Governed Execution)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATA & EXTERNAL DISPATCH                           │
│  🗄️ SQLite DB  │  💼 Azyntrix REST API  │  📧 Gmail  │  📱 WhatsApp/WS  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3.2 RESEARCH METHODOLOGY

### 3.2.1 System Architecture / Block Diagram

The system architecture consists of five decoupled layers working synchronously:

```
[ Layer 1: Client Application Layer ]
 ├── CEO Mobile App (React 18 / Vite / Tailwind / Dark Mode Glassmorphism)
 ├── Enterprise HRMS Portal (React 18 / Vite / Lucide Icons / Recharts)
 └── Employee Self-Service Portal (Leave, Clock-in & Digital Payslips)
            │
            ▼ (HTTP / SSE / WebSocket)
[ Layer 2: API Gateway & Streaming Layer ]
 ├── FastAPI Router (/api/v1/orchestration)
 ├── Real-Time Server-Sent Events (SSE) Token Streaming
 └── IST Time Context Injector (UTC+5:30) & Session State Management
            │
            ▼
[ Layer 3: LangGraph Multi-Agent Orchestration Fabric ]
 ├── Supervisor Intent Router Node (State Classifier)
 ├── Recruitment Lead & JD Builder Agent
 ├── Payroll & Financial Disbursement Agent
 ├── HR Data Analyst & SQL Gateway Agent
 └── Policy & Compliance RAG Search Agent
            │
            ▼
[ Layer 4: Tool Execution & External Integration Gateway ]
 ├── Guarded Read-Only SQL Tool (hrms.db)
 ├── Azyntrix Career Portal API Integration (http://localhost:5050/api/v1/agent/jobs)
 ├── Google OAuth2 Gmail API Client (Interview Invites, Offer Packages)
 └── Multi-Channel Alert Gateway (WhatsApp Webhooks & WebSockets)
            │
            ▼
[ Layer 5: Data Persistence & Auditing Layer ]
 ├── Primary SQLite Enterprise Database (hrms.db)
 ├── Supabase Cloud PostgreSQL Sync (Unified Chat History)
 └── In-Memory Workflow Checkpointing (LangGraph MemorySaver)
```

#### Detailed Layer Functionality:
1. **Client Application Layer**: Delivers tailored user interfaces for CEOs, HR managers, and employees. The CEO Mobile Chat app utilizes a compact 92vh frame mode with collapsible JD review cards.
2. **API Gateway**: Exposes FastAPI endpoints (`/stream`, `/execute`, `/workflows/{id}/approve`, `/workflows/{id}/revise`). It injects real-time Indian Standard Time (`datetime.timezone(datetime.timedelta(hours=5, minutes=30))`) into every incoming request.
3. **Multi-Agent Fabric**: Built on LangGraph state machines (`HRMSAgentState`), managing state transitions between intent routing, data analysis, RAG lookup, and approval gates.
4. **Tool Execution Layer**: Houses governed function calls bound to agents. Database tools utilize parameterized queries to eliminate SQL injection risks.
5. **Persistence Layer**: Ensures state durability across system restarts using SQLite and cloud Supabase sync.

---

### 3.2.2 Design Details & Algorithms

#### Algorithm 1: Supervisor Intent Classification & Dynamic Routing
```python
Input : User Query String Q, Initiator Role R, Channel C
Output: Route Decision D ∈ {POLICY_RAG, HITL_ACTION, HR_ANALYST, RECRUITMENT}, Agent Node A

1:  Q_lower ← ToLowerCase(Q)
2:  Context ← GetTimeContext(Timezone="Asia/Kolkata")
3:  if Q_lower contains ["run payroll", "execute payroll", "approve all leaves", "terminate"] then
4:      D ← "HITL_ACTION"
5:      A ← "HITL Gate Node"
6:      ActionPayload ← CreateApprovalPayload(Action="Batch Disbursement", Risk="CRITICAL")
7:      return State(Status="WAITING_FOR_APPROVAL", Approval=ActionPayload, Agent=A)
8:  else if Q_lower contains ["jd", "job description", "recruit", "hire", "candidate", "engineer"] then
9:      D ← "RECRUITMENT"
10:     A ← "Recruitment Agent Node"
11:     RoleTitle ← ExtractRoleTitle(Q_lower)
12:     Artifact ← BuildJobDescriptionArtifact(RoleTitle, Department="Engineering", Currency="INR (₹)")
13:     ActionPayload ← CreateApprovalPayload(Action="Approve & Post JD to Azyntrix", Risk="HIGH")
14:     return State(Status="WAITING_FOR_APPROVAL", Artifact=Artifact, Approval=ActionPayload, Agent=A)
15: else if Q_lower contains ["policy", "leave rule", "carry forward", "handbook", "posh", "timing"] then
16:     D ← "POLICY_RAG"
17:     A ← "Policy RAG Node"
18:     return State(Status="RUNNING", Agent=A)
19: else
20:     D ← "HR_ANALYST"
21:     A ← "HR Data Analyst Node"
22:     return State(Status="RUNNING", Agent=A)
23: end if
```

---

#### Algorithm 2: Autonomous Job Description Posting & Azyntrix Web Dispatch
```python
Input : Workflow ID W_id, Executive Approval Action "APPROVE"
Output: Success Status S, Azyntrix Job ID Job_id, Next Chat Confirmation Message M

1:  Workflow ← LoadWorkflowFromState(W_id)
2:  if Workflow is NULL or Workflow.Status != "WAITING_FOR_APPROVAL" then
3:      return Error("Workflow not awaiting authorization")
4:  end if

5:  Artifact ← Workflow.Artifact
6:  RoleTitle ← Artifact.Content.role_title
7:  Dept ← Artifact.Content.department
8:  SalaryINR ← Artifact.Content.salary_range   // e.g. "₹ 14,00,000 - ₹ 22,00,000 / year (₹ 14 - 22 LPA)"

9:  // Step 1: Persist Requisition to Enterprise Database (hrms.db)
10: DB_Result ← SQLiteExecute("INSERT INTO job_openings (id, title, department, status, salary_min, salary_max) VALUES (?, ?, ?, ?, ?, ?)", [W_id, RoleTitle, Dept, "OPEN", 1400000, 2200000])

11: // Step 2: Autonomously Dispatch Payload to Azyntrix Careers Website API
12: AzyntrixPayload ← {
        "title": RoleTitle,
        "department": Dept,
        "description": Artifact.RawMarkdown,
        "salaryRange": SalaryINR,
        "location": "Bangalore / Remote",
        "type": "Full-Time",
        "isActive": true
    }
13: Response ← HTTP_POST("http://localhost:5050/api/v1/agent/jobs", Headers={"X-Agent-Key": "azyntrix-agent-dev-key-2026"}, JSON=AzyntrixPayload)

14: if Response.StatusCode in [200, 201] then
15:     Job_id ← Response.JSON.data.id
16:     Workflow.Status ← "COMPLETED"
17:     Artifact.Status ← "APPROVED"
18:     SendWhatsAppAlert(CEO_Phone, Title="🚀 JOB POSTED LIVE: " + RoleTitle, Summary="JD approved & live on Azyntrix Careers Board.")
19:     M ← "🎉 **" + RoleTitle + "** Job Description has been approved and **AUTONOMOUSLY POSTED to the Azyntrix Careers Website!**\n\nLive Listing: http://localhost:5180/careers"
20:     return Success(WorkflowID=W_id, JobID=Job_id, Message=M)
21: else
22:     return Error("Azyntrix REST API dispatch failed")
23: end if
```

---

## 3.3 HARDWARE AND SOFTWARE REQUIREMENTS

The operational specifications required to build, deploy, and execute the Niyukti Multi-Agent HRMS Platform are outlined below:

### 3.3.1 Software Requirements Matrix

| Category | Component / Library | Version / Specifications | Purpose |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10/11 / Ubuntu Linux | 64-bit Architecture | Base OS environment |
| **Backend Runtime** | Python | v3.11.x / v3.12.x | High-performance asynchronous execution |
| **Web Framework** | FastAPI / Uvicorn | v0.109.x / v0.27.x | ASGI API gateway & Server-Sent Events (SSE) |
| **Agentic Framework** | LangGraph / LangChain | v0.2.x / v0.3.x | Stateful multi-agent state machines & checkpointing |
| **LLM Gateway** | Google Gemini 1.5/3.6 Flash & Groq | API Gateway | Generative AI reasoning & function calling |
| **Frontend Framework** | React / Vite / TypeScript | v18.3.x / v6.x / v5.6.x | Mobile app & web workspace UI |
| **Styling & Icons** | TailwindCSS / Lucide-React | v3.4.x / v0.468.x | Dark mode glassmorphism UI & icons |
| **Primary Database** | SQLite (via `aiosqlite`) | v3.40+ | Local enterprise ACID transactional database |
| **Cloud History Sync** | Supabase PostgreSQL | Cloud Client v2.x | Multi-device chat history synchronization |
| **External Integration** | Node.js (Azyntrix Backend) | v20.x LTS | External Careers Portal REST API on Port 5050 |

---

### 3.3.2 Hardware Requirements Matrix

| Parameter | Minimum Requirement | Recommended Specification |
| :--- | :--- | :--- |
| **Processor (CPU)** | Dual-Core Intel Core i5 / AMD Ryzen 5 (2.4 GHz) | Quad-Core / Octa-Core Intel Core i7 / AMD Ryzen 7 |
| **System Memory (RAM)** | 8 GB DDR4 | 16 GB DDR4/DDR5 |
| **Storage (SSD)** | 20 GB available NVMe / SSD storage | 50 GB NVMe M.2 SSD |
| **Network Interface** | 10/100 Mbps Broadband Connection | 100+ Mbps High-Speed Fiber (for real-time SSE & LLM API calls) |
| **Display Resolution** | 1366 × 768 (Laptop) | 1920 × 1080 (FHD) or Dual Monitor Setup |
