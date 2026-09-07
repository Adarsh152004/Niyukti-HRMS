"""
HRMS Agent Roster — All 24 planned autonomous HR agents.

This module defines the HRAgentRole enum listing every planned HRMS agent.
Individual agent implementations are NOT created in Node 1.

The roster establishes the domain contracts required so:
- The agent registry knows what roles are valid
- Governance policies can reference specific agent roles
- Permission scopes can be defined per role
- Tests can verify roster completeness
"""

from __future__ import annotations

from enum import StrEnum


class HRAgentRole(StrEnum):
    """
    Enumeration of all 24 planned autonomous HR agents.

    Each agent will be implemented in a subsequent node.
    Node 1 establishes only the domain contracts.

    Agent Groups:
        Strategic:    CEO/HR Executive, HR Manager
        Recruitment:  Recruitment, Resume Screening, Candidate Ranking, Interview Coordination
        Employee:     Employee Management, Attendance, Leave Management
        Compensation: Payroll
        Performance:  Performance Management, Skill Gap Analysis
        Development:  Learning & Training, Career Development
        Retention:    Attrition Prediction, Employee Retention, Sentiment Analysis
        Analytics:    HR Analytics
        Compliance:   HR Policy, Compliance/Governance, Audit
        Planning:     Workforce Planning
        Support:      Notification, Employee HR Assistant
    """

    # ── Strategic ─────────────────────────────────────────────────────────────
    CEO_HR_EXECUTIVE_AGENT = "CEO_HR_EXECUTIVE_AGENT"
    """
    Top-level strategic agent. Processes CEO/executive commands and coordinates
    other agents. Has the highest autonomy ceiling but is always governance-bound.
    """

    HR_MANAGER_AGENT = "HR_MANAGER_AGENT"
    """
    Day-to-day HR management coordination. Delegates to specialized agents
    and handles escalations from lower-level agents.
    """

    # ── Recruitment ───────────────────────────────────────────────────────────
    RECRUITMENT_AGENT = "RECRUITMENT_AGENT"
    """
    Manages the end-to-end recruitment pipeline. Coordinates Resume Screening,
    Candidate Ranking, and Interview Coordination agents.
    """

    RESUME_SCREENING_AGENT = "RESUME_SCREENING_AGENT"
    """
    Parses and screens resumes against job requirements.
    Can read: recruitment data, resumes.
    Cannot: modify payroll, access unrelated employee data.
    """

    CANDIDATE_RANKING_AGENT = "CANDIDATE_RANKING_AGENT"
    """
    Ranks candidates for a job using AI scoring.
    Produces AIDecision records with explainable evidence.
    Candidate rejection requires human approval.
    """

    INTERVIEW_COORDINATION_AGENT = "INTERVIEW_COORDINATION_AGENT"
    """
    Autonomously schedules interviews based on availability.
    Uses Calendar adapter. Can schedule — cannot decide interview outcomes.
    """

    # ── Employee Management ───────────────────────────────────────────────────
    EMPLOYEE_MANAGEMENT_AGENT = "EMPLOYEE_MANAGEMENT_AGENT"
    """
    Manages employee lifecycle events (onboarding, transfers, offboarding).
    Employee termination always requires human approval.
    """

    ATTENDANCE_AGENT = "ATTENDANCE_AGENT"
    """
    Processes attendance records, identifies anomalies, handles regularization requests.
    """

    LEAVE_MANAGEMENT_AGENT = "LEAVE_MANAGEMENT_AGENT"
    """
    Processes leave requests based on policy. Routes approvals through workflow.
    """

    # ── Compensation ──────────────────────────────────────────────────────────
    PAYROLL_AGENT = "PAYROLL_AGENT"
    """
    Analyzes payroll data and prepares payroll runs.
    Can analyze payroll, can prepare payroll actions.
    CANNOT terminate employees or modify HR policies.
    Payroll modification requires human approval.
    """

    # ── Performance ───────────────────────────────────────────────────────────
    PERFORMANCE_MANAGEMENT_AGENT = "PERFORMANCE_MANAGEMENT_AGENT"
    """
    Tracks KPIs, manages review cycles, generates performance predictions.
    Promotion recommendations require human approval.
    """

    SKILL_GAP_ANALYSIS_AGENT = "SKILL_GAP_ANALYSIS_AGENT"
    """
    Analyzes skill gaps between current employee skills and role requirements.
    Feeds recommendations to the Learning & Training agent.
    """

    # ── Learning & Development ────────────────────────────────────────────────
    LEARNING_TRAINING_AGENT = "LEARNING_TRAINING_AGENT"
    """
    Recommends and manages training programs based on skill gaps.
    Can autonomously enroll employees in approved training programs.
    """

    CAREER_DEVELOPMENT_AGENT = "CAREER_DEVELOPMENT_AGENT"
    """
    Creates career development plans aligned with employee goals and org needs.
    """

    # ── Retention ─────────────────────────────────────────────────────────────
    ATTRITION_PREDICTION_AGENT = "ATTRITION_PREDICTION_AGENT"
    """
    Predicts employee attrition risk using multiple signals.
    Produces AIDecision records. High-risk predictions trigger retention agent.
    """

    EMPLOYEE_RETENTION_AGENT = "EMPLOYEE_RETENTION_AGENT"
    """
    Generates retention action recommendations for high-attrition-risk employees.
    Actions require HR manager approval before execution.
    """

    SENTIMENT_ANALYSIS_AGENT = "SENTIMENT_ANALYSIS_AGENT"
    """
    Analyzes employee sentiment from surveys, feedback, and communication (with consent).
    PII access is strictly limited — aggregate analysis preferred.
    """

    # ── Analytics ─────────────────────────────────────────────────────────────
    HR_ANALYTICS_AGENT = "HR_ANALYTICS_AGENT"
    """
    Generates HR reports and analytics dashboards on demand.
    Can answer CEO queries like 'show departments with productivity decline'.
    """

    # ── Compliance & Governance ───────────────────────────────────────────────
    HR_POLICY_AGENT = "HR_POLICY_AGENT"
    """
    Enforces HR policies during governance checks.
    Policy modifications always require CEO/HR_ADMIN approval.
    """

    COMPLIANCE_GOVERNANCE_AGENT = "COMPLIANCE_GOVERNANCE_AGENT"
    """
    Monitors for compliance violations across all HR modules.
    Can block actions that violate policy — cannot modify policies.
    """

    AUDIT_AGENT = "AUDIT_AGENT"
    """
    Produces audit reports and monitors audit trails.
    Read-only access to all audit records. Cannot modify any data.
    """

    # ── Planning ──────────────────────────────────────────────────────────────
    WORKFORCE_PLANNING_AGENT = "WORKFORCE_PLANNING_AGENT"
    """
    Strategic workforce planning — headcount forecasting, succession planning.
    Recommendations require HR_ADMIN approval.
    """

    # ── Support & Communication ───────────────────────────────────────────────
    NOTIFICATION_AGENT = "NOTIFICATION_AGENT"
    """
    Dispatches notifications across all channels (email, SMS, in-app, WhatsApp).
    Cannot access PII beyond recipient contact references.
    """

    EMPLOYEE_HR_ASSISTANT = "EMPLOYEE_HR_ASSISTANT"
    """
    Conversational HR assistant for employees.
    Can access ONLY the authenticated employee's own authorized data.
    Cannot access other employees' data under any circumstances.
    """
