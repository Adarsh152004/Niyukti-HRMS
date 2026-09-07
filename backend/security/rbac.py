"""
Security — Role-Based Access Control (RBAC) contracts.

Defines the 8 HRMS roles, permission model, and RBAC context.

IMPORTANT: AI_AGENT role never receives unrestricted permissions.
Agent permissions are always explicitly scoped via AgentPermissionScope.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class HRMSRole(StrEnum):
    """
    HRMS role definitions.

    Roles:
        SUPER_ADMIN:  Full platform access. Can modify system configuration.
        CEO:          Strategic access. Can issue commands across all modules.
                      Can approve CRITICAL-risk actions.
        HR_ADMIN:     Full HR module access. Can configure workflows and policies.
                      Can approve HIGH-risk actions.
        HR_MANAGER:   Day-to-day HR operations. Can approve MEDIUM-risk actions.
        MANAGER:      Department-level access. Approves leave, reviews performance.
        EMPLOYEE:     Self-service access. Own data only.
        AUDITOR:      Read-only access to audit logs and reports. No write access.
        AI_AGENT:     Restricted programmatic access. Scope defined per agent.
                      NEVER receives unrestricted permissions automatically.
    """

    SUPER_ADMIN = "SUPER_ADMIN"
    CEO = "CEO"
    HR_ADMIN = "HR_ADMIN"
    HR_MANAGER = "HR_MANAGER"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"
    AUDITOR = "AUDITOR"
    AI_AGENT = "AI_AGENT"

    @property
    def can_approve_critical(self) -> bool:
        """Return True if this role can approve CRITICAL-risk actions."""
        return self in (HRMSRole.SUPER_ADMIN, HRMSRole.CEO)

    @property
    def can_approve_high(self) -> bool:
        """Return True if this role can approve HIGH-risk actions."""
        return self in (HRMSRole.SUPER_ADMIN, HRMSRole.CEO, HRMSRole.HR_ADMIN)

    @property
    def can_approve_medium(self) -> bool:
        """Return True if this role can approve MEDIUM-risk actions."""
        return self in (
            HRMSRole.SUPER_ADMIN,
            HRMSRole.CEO,
            HRMSRole.HR_ADMIN,
            HRMSRole.HR_MANAGER,
        )

    @property
    def is_human_role(self) -> bool:
        """Return True if this role represents a human actor."""
        return self != HRMSRole.AI_AGENT

    @property
    def privilege_level(self) -> int:
        """Numeric privilege level for ordering (higher = more privileged)."""
        levels = {
            HRMSRole.SUPER_ADMIN: 100,
            HRMSRole.CEO: 90,
            HRMSRole.HR_ADMIN: 70,
            HRMSRole.HR_MANAGER: 60,
            HRMSRole.MANAGER: 50,
            HRMSRole.AUDITOR: 30,
            HRMSRole.EMPLOYEE: 20,
            HRMSRole.AI_AGENT: 10,
        }
        return levels.get(self, 0)


class Permission(StrEnum):
    """
    Fine-grained permissions within the HRMS platform.

    Permissions are assigned to roles via RBACPolicy.
    """

    # Employee
    EMPLOYEE_READ = "employee:read"
    EMPLOYEE_WRITE = "employee:write"
    EMPLOYEE_DELETE = "employee:delete"
    EMPLOYEE_PII_READ = "employee:pii:read"

    # Recruitment
    RECRUITMENT_READ = "recruitment:read"
    RECRUITMENT_WRITE = "recruitment:write"
    RESUME_PARSE = "resume:parse"
    CANDIDATE_RANK = "candidate:rank"
    CANDIDATE_REJECT = "candidate:reject"

    # Attendance & Leave
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_WRITE = "attendance:write"
    LEAVE_READ = "leave:read"
    LEAVE_APPROVE = "leave:approve"

    # Payroll
    PAYROLL_READ = "payroll:read"
    PAYROLL_WRITE = "payroll:write"
    PAYROLL_APPROVE = "payroll:approve"

    # Performance
    PERFORMANCE_READ = "performance:read"
    PERFORMANCE_WRITE = "performance:write"
    PERFORMANCE_REVIEW_APPROVE = "performance:review:approve"

    # Training
    TRAINING_READ = "training:read"
    TRAINING_WRITE = "training:write"

    # Analytics & Reports
    ANALYTICS_READ = "analytics:read"
    REPORTS_READ = "reports:read"
    REPORTS_GENERATE = "reports:generate"

    # AI / Agents
    AGENT_STATUS_READ = "agent:status:read"
    AGENT_CONTROL = "agent:control"
    AUTONOMY_CONFIGURE = "autonomy:configure"
    AI_DECISION_READ = "ai:decision:read"

    # Governance
    APPROVAL_READ = "approval:read"
    APPROVAL_GRANT = "approval:grant"
    HITL_RESPOND = "hitl:respond"
    POLICY_READ = "policy:read"
    POLICY_WRITE = "policy:write"

    # Audit
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"

    # System
    SYSTEM_ADMIN = "system:admin"
    EMERGENCY_STOP = "emergency:stop"


# Default permission sets per role
ROLE_PERMISSIONS: dict[HRMSRole, set[Permission]] = {
    HRMSRole.SUPER_ADMIN: set(Permission),  # All permissions
    HRMSRole.CEO: {
        Permission.EMPLOYEE_READ,
        Permission.RECRUITMENT_READ,
        Permission.ATTENDANCE_READ,
        Permission.LEAVE_READ,
        Permission.PAYROLL_READ,
        Permission.PAYROLL_APPROVE,
        Permission.PERFORMANCE_READ,
        Permission.TRAINING_READ,
        Permission.ANALYTICS_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_GENERATE,
        Permission.AGENT_STATUS_READ,
        Permission.AGENT_CONTROL,
        Permission.AUTONOMY_CONFIGURE,
        Permission.AI_DECISION_READ,
        Permission.APPROVAL_READ,
        Permission.APPROVAL_GRANT,
        Permission.HITL_RESPOND,
        Permission.POLICY_READ,
        Permission.AUDIT_READ,
        Permission.EMERGENCY_STOP,
    },
    HRMSRole.HR_ADMIN: {
        Permission.EMPLOYEE_READ,
        Permission.EMPLOYEE_WRITE,
        Permission.EMPLOYEE_PII_READ,
        Permission.RECRUITMENT_READ,
        Permission.RECRUITMENT_WRITE,
        Permission.RESUME_PARSE,
        Permission.CANDIDATE_RANK,
        Permission.CANDIDATE_REJECT,
        Permission.ATTENDANCE_READ,
        Permission.ATTENDANCE_WRITE,
        Permission.LEAVE_READ,
        Permission.LEAVE_APPROVE,
        Permission.PAYROLL_READ,
        Permission.PAYROLL_WRITE,
        Permission.PAYROLL_APPROVE,
        Permission.PERFORMANCE_READ,
        Permission.PERFORMANCE_WRITE,
        Permission.TRAINING_READ,
        Permission.TRAINING_WRITE,
        Permission.ANALYTICS_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_GENERATE,
        Permission.AGENT_STATUS_READ,
        Permission.AI_DECISION_READ,
        Permission.APPROVAL_READ,
        Permission.APPROVAL_GRANT,
        Permission.HITL_RESPOND,
        Permission.POLICY_READ,
        Permission.POLICY_WRITE,
        Permission.AUDIT_READ,
    },
    HRMSRole.HR_MANAGER: {
        Permission.EMPLOYEE_READ,
        Permission.EMPLOYEE_WRITE,
        Permission.RECRUITMENT_READ,
        Permission.RECRUITMENT_WRITE,
        Permission.RESUME_PARSE,
        Permission.CANDIDATE_RANK,
        Permission.ATTENDANCE_READ,
        Permission.LEAVE_READ,
        Permission.LEAVE_APPROVE,
        Permission.PAYROLL_READ,
        Permission.PERFORMANCE_READ,
        Permission.PERFORMANCE_WRITE,
        Permission.TRAINING_READ,
        Permission.ANALYTICS_READ,
        Permission.REPORTS_READ,
        Permission.AGENT_STATUS_READ,
        Permission.AI_DECISION_READ,
        Permission.APPROVAL_READ,
        Permission.APPROVAL_GRANT,
        Permission.HITL_RESPOND,
        Permission.POLICY_READ,
        Permission.AUDIT_READ,
    },
    HRMSRole.MANAGER: {
        Permission.EMPLOYEE_READ,
        Permission.ATTENDANCE_READ,
        Permission.LEAVE_READ,
        Permission.LEAVE_APPROVE,
        Permission.PERFORMANCE_READ,
        Permission.PERFORMANCE_WRITE,
        Permission.TRAINING_READ,
        Permission.REPORTS_READ,
        Permission.APPROVAL_READ,
        Permission.HITL_RESPOND,
    },
    HRMSRole.EMPLOYEE: {
        Permission.EMPLOYEE_READ,  # Own data only — enforced at data layer
        Permission.ATTENDANCE_READ,
        Permission.LEAVE_READ,
        Permission.PAYROLL_READ,  # Own payslips only
        Permission.PERFORMANCE_READ,  # Own reviews only
        Permission.TRAINING_READ,
    },
    HRMSRole.AUDITOR: {
        Permission.EMPLOYEE_READ,
        Permission.ATTENDANCE_READ,
        Permission.PAYROLL_READ,
        Permission.PERFORMANCE_READ,
        Permission.ANALYTICS_READ,
        Permission.REPORTS_READ,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
        Permission.AI_DECISION_READ,
        Permission.APPROVAL_READ,
        Permission.POLICY_READ,
    },
    HRMSRole.AI_AGENT: set(),  # No default permissions — must be explicitly scoped
}


class RBACContext(BaseModel):
    """
    RBAC evaluation context for a specific actor and requested permission.
    """

    actor_id: str
    actor_role: HRMSRole
    requested_permission: Permission
    resource_type: str | None = Field(default=None)
    resource_id: str | None = Field(default=None)
    department_id: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RBACPolicy(BaseModel):
    """
    Configured RBAC policy for a specific role and resource combination.

    More specific policies override broader ones.
    """

    policy_id: str
    role: HRMSRole
    permissions: set[Permission] = Field(default_factory=set)
    resource_type: str | None = Field(default=None)
    resource_id: str | None = Field(default=None)
    department_id: str | None = Field(default=None)
    is_active: bool = Field(default=True)

    def has_permission(self, permission: Permission) -> bool:
        """Check if this policy grants a specific permission."""
        return permission in self.permissions
