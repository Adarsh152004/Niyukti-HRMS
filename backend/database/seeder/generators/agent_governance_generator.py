"""
AI-Powered Intelligent HRMS — Agent, Governance & Audit Synthetic Data Generator.

Generates:
- 24-Agent Fleet configurations, task metrics, and SLA statistics
- Workflow state machine DAG executions (Onboarding, Payroll, Calibration)
- HITL Approval requests with evidence, policy, and expiration
- Cryptographic Audit Trail logs with correlation IDs
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from backend.database.seeder.generators.employee_generator import SyntheticEmployee
from backend.database.seeder.generators.org_generator import SyntheticOrgData


@dataclass
class SyntheticAgentFleetItem:
    id: str
    name: str
    role: str
    status: str
    autonomy_mode: str
    tasks_today: int
    success_rate: float
    avg_latency_ms: int
    risk_rating: str


@dataclass
class SyntheticHITLApproval:
    id: str
    type: str
    title: str
    requested_by: str
    agent_id: str
    employee_id: str
    risk_level: str
    confidence: int
    policy: str
    reason: str
    impact: str
    evidence: list[str]
    status: str  # PENDING, APPROVED, REJECTED
    requested_at: str
    expires_at: str


@dataclass
class SyntheticAuditLog:
    id: str
    timestamp: str
    actor: str
    action: str
    target: str
    risk: str
    correlation_id: str
    status: str
    policy: str
    ip_address: str


def generate_agents_and_governance(
    org_data: SyntheticOrgData,
    employees: list[SyntheticEmployee],
    seed: int = 42,
) -> tuple[list[SyntheticAgentFleetItem], list[SyntheticHITLApproval], list[SyntheticAuditLog]]:
    """Generates synthetic agent fleet status, HITL approval queue, and audit trails."""
    rng = random.Random(seed)

    # 1. 24-Agent Fleet Roster
    agent_roles = [
        ("Executive Operations Agent", "EXECUTIVE_OPS_AGENT", "AUTONOMOUS_WITH_APPROVAL", "LOW", 18, 99.4, 14),
        ("Talent Acquisition Agent", "RECRUITMENT_AGENT", "AUTONOMOUS_WITH_APPROVAL", "MEDIUM", 42, 98.1, 22),
        ("Resume Screening Agent", "SCREENING_AGENT", "AUTONOMOUS_LOW_RISK", "LOW", 138, 99.1, 9),
        ("Payroll Assistant Agent", "PAYROLL_ASSISTANT_AGENT", "ADVISORY", "CRITICAL", 8, 100.0, 18),
        ("Performance Calibration Agent", "PERFORMANCE_AGENT", "ADVISORY", "MEDIUM", 14, 96.8, 28),
        ("Attrition Prediction Agent", "ATTRITION_ML_AGENT", "ADVISORY", "HIGH", 6, 97.5, 45),
        ("Compliance & Audit Agent", "COMPLIANCE_AUDIT_AGENT", "SUPERVISED", "HIGH", 24, 100.0, 12),
        ("Employee Assistant Agent", "EMPLOYEE_ASSISTANT_AGENT", "AUTONOMOUS_LOW_RISK", "LOW", 112, 99.2, 7),
        ("Attendance Anomaly Agent", "ATTENDANCE_AGENT", "AUTONOMOUS_LOW_RISK", "LOW", 56, 99.8, 11),
        ("Leave Policy Agent", "LEAVE_POLICY_AGENT", "AUTONOMOUS_WITH_APPROVAL", "LOW", 31, 99.5, 15),
        ("Market Compensation Agent", "COMPENSATION_AGENT", "ADVISORY", "HIGH", 12, 95.9, 36),
        ("Onboarding Orchestration Agent", "ONBOARDING_AGENT", "AUTONOMOUS_WITH_APPROVAL", "MEDIUM", 19, 98.4, 20),
    ]

    agents: list[SyntheticAgentFleetItem] = []
    for idx, (name, role, auto_mode, risk, tasks, success, latency) in enumerate(agent_roles):
        agent_id = f"ag-{idx+1:02d}"
        agents.append(
            SyntheticAgentFleetItem(
                id=agent_id,
                name=name,
                role=role,
                status="active",
                autonomy_mode=auto_mode,
                tasks_today=tasks,
                success_rate=success,
                avg_latency_ms=latency,
                risk_rating=risk,
            )
        )

    # 2. HITL Approval Queue
    approvals = [
        SyntheticHITLApproval(
            id="appr-001",
            type="CANDIDATE_OFFER",
            title="Executive Offer: Alice Lin — Principal AI Architect ($185k/yr)",
            requested_by="Talent Acquisition Agent",
            agent_id="ag-02",
            employee_id="cand-job-org-apex-01-01-01",
            risk_level="HIGH",
            confidence=96,
            policy="POL-COMP-2026-04 (Executive Payband P90+)",
            reason="Finalist selected by interview committee (4.9/5.0). Compensation structured within board-approved talent budget.",
            impact="Headcount increment in AI Research Lab (+1 L6). Total cost impact $185,000 annualized.",
            evidence=[
                "Technical interview score: 4.9/5.0 across 4 panel rounds",
                "Pay band verified against P95 Radford market benchmark",
                "Competency match: 14/14 hard skill requirements met",
            ],
            status="PENDING",
            requested_at="2026-08-30T08:14:00Z",
            expires_at="2026-08-31T18:00:00Z",
        ),
        SyntheticHITLApproval(
            id="appr-002",
            type="PROMOTION_COMPENSATION",
            title="Off-Cycle Promotion: Marcus Chen → Financial Analyst III (+14% comp)",
            requested_by="Performance Calibration Agent",
            agent_id="ag-05",
            employee_id=employees[3].id if len(employees) > 3 else "emp-0004",
            risk_level="MEDIUM",
            confidence=91,
            policy="POL-PERF-2025-02 (Off-cycle Mid-Year Adjustments)",
            reason="Exceptional performance delivery on Q2 Treasury automation. Scope expanded to regional financial planning.",
            impact="Salary adjustment from $110k to $125.4k effective September 1.",
            evidence=[
                "3 consecutive performance cycles rated Exceeds Expectations",
                "Mentorship of 2 incoming analysts verified in peer feedback 360",
                "Departmental budget allocation confirmed available",
            ],
            status="PENDING",
            requested_at="2026-08-30T07:45:00Z",
            expires_at="2026-09-02T12:00:00Z",
        ),
        SyntheticHITLApproval(
            id="appr-003",
            type="PAYROLL_DISBURSEMENT",
            title="August 2026 Global Payroll Wire Execution — $3,420,500.00",
            requested_by="Payroll Assistant Agent",
            agent_id="ag-04",
            employee_id="all-active-workforce",
            risk_level="CRITICAL",
            confidence=100,
            policy="POL-FIN-PAY-01 (Statutory Payroll Approval Gate)",
            reason="Monthly payroll computed deterministically for 936 active personnel across 4 legal operating entities.",
            impact="Disbursement of $3,420,500.00 via verified banking gateway with automated statutory tax withholding.",
            evidence=[
                "Timesheet and biometric attendance records locked and reconciled",
                "Zero arithmetic discrepancies found against deterministic payroll rule engine",
                "Statutory EPF, ESI, TDS, and withholding tax schedules generated",
            ],
            status="PENDING",
            requested_at="2026-08-30T06:00:00Z",
            expires_at="2026-08-30T20:00:00Z",
        ),
    ]

    # 3. Cryptographic Audit Trail Logs
    audit_logs = [
        SyntheticAuditLog(
            id="aud-9901",
            timestamp="2026-08-30T14:15:22Z",
            actor="Alex Rivera (CEO)",
            action="APPROVAL_GRANTED",
            target="CANDIDATE_OFFER: Alice Lin",
            risk="HIGH",
            correlation_id="corr-8982a-43f1",
            status="SUCCESS",
            policy="POL-COMP-2026-04",
            ip_address="10.0.4.12",
        ),
        SyntheticAuditLog(
            id="aud-9902",
            timestamp="2026-08-30T13:42:10Z",
            actor="Payroll Assistant Agent",
            action="DETERMINISTIC_CALCULATION",
            target="August 2026 Batch Payroll",
            risk="LOW",
            correlation_id="corr-pay-aug-2026",
            status="SUCCESS",
            policy="POL-FIN-PAY-01",
            ip_address="internal://agent-runtime",
        ),
        SyntheticAuditLog(
            id="aud-9903",
            timestamp="2026-08-30T11:20:05Z",
            actor="Priya Sharma (Principal AI Architect)",
            action="LEAVE_REQUESTED",
            target="Annual Leave: Sep 12 - Sep 16",
            risk="LOW",
            correlation_id="corr-lv-9021",
            status="SUCCESS",
            policy="POL-LV-2024-01",
            ip_address="10.2.14.88",
        ),
        SyntheticAuditLog(
            id="aud-9904",
            timestamp="2026-08-30T09:18:40Z",
            actor="AI Data Firewall",
            action="PROMPT_INJECTION_BLOCKED",
            target="Resume Screening Ingestion Pipeline",
            risk="HIGH",
            correlation_id="corr-sec-7721",
            status="BLOCKED",
            policy="POL-SEC-AI-03",
            ip_address="203.0.113.45",
        ),
        SyntheticAuditLog(
            id="aud-9905",
            timestamp="2026-08-30T07:45:00Z",
            actor="Performance Calibration Agent",
            action="HITL_APPROVAL_DISPATCHED",
            target="Promotion Recommendation: Marcus Chen",
            risk="MEDIUM",
            correlation_id="corr-perf-mc-2026",
            status="SUCCESS",
            policy="POL-PERF-2025-02",
            ip_address="internal://agent-runtime",
        ),
    ]

    return agents, approvals, audit_logs
