# MCP & Tool Fabric Architecture: Program 5

## 1. Overview

Program 5 implements the enterprise Model Context Protocol (MCP) client, 9 internal MCP servers, native multi-provider LLM adapters (OpenAI, Anthropic, Gemini, Local, Mock), a 6-layer defense-in-depth security guardrail stack, a token-budgeted context window manager, and the unified `AgentRuntimeGateway`.

```
Human / Agent / System
        ↓
AgentRuntimeGateway
        ↓
Context Window Manager (Token Budgeted & Prioritized)
        ↓
Input & Context Guardrails (Layers 1 & 2)
        ↓
AI Gateway Multi-Provider Dispatch (OpenAI, Anthropic, Gemini, Local, Mock)
        ↓
Structured Tool Call Proposal
        ↓
Tool Guardrail (Layer 3)
        ↓
MCP Client ──► 9 Internal MCP Servers (HRMS, Knowledge, Analytics, Workflow, etc.)
        ↓
Action Guardrail & HITL Gating (Layer 5)
        ↓
CommandBus & ActionExecutor
        ↓
Output Guardrail & Runtime Guardrail (Layers 4 & 6)
        ↓
Outcome
```

---

## 2. Six-Layer Guardrail Stack

1. **Input Guardrail (`Layer 1`)**: Intercepts direct prompt injection, developer-mode jailbreaks, and adversarial system overrides.
2. **Context Guardrail (`Layer 2`)**: Guarantees zero cross-tenant contamination and blocks unmasked API keys or credentials.
3. **Tool Guardrail (`Layer 3`)**: Enforces tool registry whitelists and blocks arbitrary SQL (`sql.execute`, `drop table`), shell, or raw Python execution.
4. **Output Guardrail (`Layer 4`)**: Strips PII identifiers via `AIDataFirewall` and detects hallucinated mutation claims.
5. **Action Guardrail (`Layer 5`)**: Identifies high-risk mutation operations (e.g. employee termination, salary altering) and mandates Human-In-The-Loop approval.
6. **Runtime Guardrail (`Layer 6`)**: Monitors loop counters, tool call limits, delegation depths, and monetary budgets.

---

## 3. The 9 Internal MCP Servers

| Server ID | Name | Core Tools | Security Classification |
| :--- | :--- | :--- | :--- |
| `hrms-server` | HRMS Core MCP Server | `hrms.get_employee`, `hrms.list_employees` | Read-only |
| `knowledge-server` | Knowledge & Policy MCP Server | `knowledge.search_policies` | Read-only / ACL Scoped |
| `analytics-server` | HR Analytics MCP Server | `analytics.get_headcount_stats` | Read-only |
| `workflow-server` | Workflow Engine MCP Server | `workflow.get_instance_status` | Read-only |
| `document-server` | Document Intelligence MCP Server | `document.extract_metadata` | Read-only |
| `recruitment-server` | Recruitment ATS MCP Server | `recruitment.get_job_requisition` | Read-only |
| `payroll-server` | Payroll Read-Only MCP Server | `payroll.explain_payslip_breakdown` | Read-only / Zero Mutation |
| `notification-server`| Notification Dispatch MCP Server | `notification.dispatch_template` | Governed Write |
| `reporting-server` | Executive Reporting MCP Server | `reporting.build_executive_summary` | Read-only |

---

## 4. Context Window Assembly Pipeline

Context is formed strictly following priority quotas:
$$\text{SYSTEM} + \text{SECURITY} + \text{AGENT POLICY} + \text{TASK} + \text{PLAN} + \text{MEMORY} + \text{RAG} + \text{TOOLS} + \text{RECENT RESULTS}$$

- **Safety Invariant**: Security boundaries and Agent Policies are non-truncatable (Priority 100).
- **Sliding Window**: Memory items and tool results are dynamically trimmed when nearing model context token limits.
