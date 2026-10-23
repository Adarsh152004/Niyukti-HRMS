"""Tests — RBAC Roles and Permissions."""

from backend.security.rbac import ROLE_PERMISSIONS, HRMSRole, Permission, RBACPolicy


def test_hrms_role_count():
    """There must be exactly 8 HRMS roles."""
    assert len(HRMSRole) == 8


def test_hrms_role_values():
    roles = [r.value for r in HRMSRole]
    assert "SUPER_ADMIN" in roles
    assert "CEO" in roles
    assert "HR_ADMIN" in roles
    assert "HR_MANAGER" in roles
    assert "MANAGER" in roles
    assert "EMPLOYEE" in roles
    assert "AUDITOR" in roles
    assert "AI_AGENT" in roles


def test_ai_agent_has_no_default_permissions():
    """AI_AGENT must never receive unrestricted permissions automatically."""
    ai_permissions = ROLE_PERMISSIONS[HRMSRole.AI_AGENT]
    assert len(ai_permissions) == 0, "AI_AGENT must have zero default permissions — scope must be explicitly granted"


def test_super_admin_has_all_permissions():
    super_admin_permissions = ROLE_PERMISSIONS[HRMSRole.SUPER_ADMIN]
    all_permissions = set(Permission)
    assert super_admin_permissions == all_permissions


def test_can_approve_critical():
    assert HRMSRole.SUPER_ADMIN.can_approve_critical
    assert HRMSRole.CEO.can_approve_critical
    assert not HRMSRole.HR_ADMIN.can_approve_critical
    assert not HRMSRole.EMPLOYEE.can_approve_critical
    assert not HRMSRole.AI_AGENT.can_approve_critical


def test_can_approve_high():
    assert HRMSRole.SUPER_ADMIN.can_approve_high
    assert HRMSRole.CEO.can_approve_high
    assert HRMSRole.HR_ADMIN.can_approve_high
    assert not HRMSRole.HR_MANAGER.can_approve_high
    assert not HRMSRole.EMPLOYEE.can_approve_high


def test_can_approve_medium():
    assert HRMSRole.HR_MANAGER.can_approve_medium
    assert not HRMSRole.MANAGER.can_approve_medium
    assert not HRMSRole.EMPLOYEE.can_approve_medium


def test_is_human_role():
    assert HRMSRole.CEO.is_human_role
    assert HRMSRole.EMPLOYEE.is_human_role
    assert not HRMSRole.AI_AGENT.is_human_role


def test_privilege_levels():
    assert HRMSRole.SUPER_ADMIN.privilege_level > HRMSRole.CEO.privilege_level
    assert HRMSRole.CEO.privilege_level > HRMSRole.HR_ADMIN.privilege_level
    assert HRMSRole.HR_ADMIN.privilege_level > HRMSRole.EMPLOYEE.privilege_level
    assert HRMSRole.EMPLOYEE.privilege_level > HRMSRole.AI_AGENT.privilege_level


def test_employee_cannot_modify_payroll():
    """EMPLOYEE role must not have payroll write permission."""
    employee_perms = ROLE_PERMISSIONS[HRMSRole.EMPLOYEE]
    assert Permission.PAYROLL_WRITE not in employee_perms


def test_payroll_agent_cannot_terminate_employees():
    """AI_AGENT has no default permissions — scope is granted per-agent."""
    ai_perms = ROLE_PERMISSIONS[HRMSRole.AI_AGENT]
    assert Permission.EMPLOYEE_DELETE not in ai_perms


def test_rbac_policy_has_permission():
    policy = RBACPolicy(
        policy_id="pol-001",
        role=HRMSRole.HR_MANAGER,
        permissions={Permission.EMPLOYEE_READ, Permission.RECRUITMENT_READ},
    )
    assert policy.has_permission(Permission.EMPLOYEE_READ)
    assert not policy.has_permission(Permission.SYSTEM_ADMIN)
