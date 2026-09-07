"""
Specialized Agent Enums — Roles, Autonomy Modes, Tool Access Levels, and Evaluation Criteria.
"""

from __future__ import annotations

from enum import StrEnum


class SpecializedAgentRole(StrEnum):
    """The 24 standard specialized AI HR agents."""

    EXECUTIVE_HR_AGENT = "EXECUTIVE_HR_AGENT"
    HR_MANAGER_AGENT = "HR_MANAGER_AGENT"
    RECRUITMENT_AGENT = "RECRUITMENT_AGENT"
    RESUME_SCREENING_AGENT = "RESUME_SCREENING_AGENT"
    CANDIDATE_RANKING_AGENT = "CANDIDATE_RANKING_AGENT"
    INTERVIEW_INTELLIGENCE_AGENT = "INTERVIEW_INTELLIGENCE_AGENT"
    EMPLOYEE_ASSISTANT_AGENT = "EMPLOYEE_ASSISTANT_AGENT"
    ONBOARDING_AGENT = "ONBOARDING_AGENT"
    OFFBOARDING_AGENT = "OFFBOARDING_AGENT"
    ATTENDANCE_AGENT = "ATTENDANCE_AGENT"
    LEAVE_MANAGEMENT_AGENT = "LEAVE_MANAGEMENT_AGENT"
    PAYROLL_ASSISTANT_AGENT = "PAYROLL_ASSISTANT_AGENT"
    PERFORMANCE_AGENT = "PERFORMANCE_AGENT"
    SKILL_GAP_AGENT = "SKILL_GAP_AGENT"
    LEARNING_AGENT = "LEARNING_AGENT"
    CAREER_COACH_AGENT = "CAREER_COACH_AGENT"
    ATTRITION_AGENT = "ATTRITION_AGENT"
    RETENTION_AGENT = "RETENTION_AGENT"
    SENTIMENT_AGENT = "SENTIMENT_AGENT"
    WORKFORCE_PLANNING_AGENT = "WORKFORCE_PLANNING_AGENT"
    HR_ANALYTICS_AGENT = "HR_ANALYTICS_AGENT"
    COMPLIANCE_AGENT = "COMPLIANCE_AGENT"
    DOCUMENT_INTELLIGENCE_AGENT = "DOCUMENT_INTELLIGENCE_AGENT"
    NOTIFICATION_AGENT = "NOTIFICATION_AGENT"


class AutonomyMode(StrEnum):
    """Operational autonomy modes for specialized agents."""

    ADVISORY = "ADVISORY"  # Analysis & recommendations only; human executes all actions
    ASSISTED = "ASSISTED"  # Prepares actions for human one-click approval
    SUPERVISED = "SUPERVISED"  # Low-risk automated actions with continuous supervisor oversight
    AUTONOMOUS_LOW_RISK = "AUTONOMOUS_LOW_RISK"  # Reversible low-risk actions execute without per-action approval
    AUTONOMOUS_WITH_APPROVAL = "AUTONOMOUS_WITH_APPROVAL"  # Autonomous discovery/prep, HITL required for final mutation
    DISABLED = "DISABLED"  # Agent disabled by administrator or safety quarantine


class ToolAccessLevel(StrEnum):
    """Access level for a specific tool in an agent's tool policy."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
