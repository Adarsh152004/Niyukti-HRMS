"""Tests — First-class AI Agent security, capabilities, and anti-impersonation invariants."""

import pytest

from backend.hrms.application.authorization import AuthorizationService, HRMSAction
from backend.hrms.domain.actor import ActorType
from backend.security.application.agent_security_service import AgentAuthenticationError, AgentSecurityService
from backend.security.domain.enums import AgentStatus


def test_agent_registration_and_independent_authentication():
    agent_svc = AgentSecurityService()
    agent = agent_svc.register_agent(
        name="Resume Screening Agent",
        organization_id="org-acme",
        capabilities=["employee.read", "resume.screen"],
    )

    assert agent.agent_id is not None
    assert agent.status == AgentStatus.ACTIVE
    assert "resume.screen" in agent.capabilities

    # Authenticate agent independently
    agent_actor = agent_svc.authenticate_agent(agent.agent_id, "org-acme")
    assert agent_actor.actor_type == ActorType.AI_AGENT
    assert agent_actor.organization_id == "org-acme"
    assert "resume.screen" in agent_actor.metadata["capabilities"]


def test_suspended_agent_authentication_blocked():
    agent_svc = AgentSecurityService()
    agent = agent_svc.register_agent(
        name="Attrition Prediction Agent",
        organization_id="org-acme",
        capabilities=["employee.read"],
    )

    # Suspend agent
    agent_svc.suspend_agent(agent.agent_id)

    # Authentication attempt must be blocked
    with pytest.raises(AgentAuthenticationError, match="blocked"):
        agent_svc.authenticate_agent(agent.agent_id, "org-acme")


def test_agent_least_privilege_and_no_human_impersonation():
    """AI Agent must use explicit capabilities and cannot execute ungranted actions."""
    auth_policy = AuthorizationService()
    agent_svc = AgentSecurityService()
    agent = agent_svc.register_agent(
        name="Candidate Ranking Agent",
        organization_id="org-acme",
        capabilities=["candidate.rank"],  # NOT employee.delete or employee.view_salary
    )

    agent_actor = agent_svc.authenticate_agent(agent.agent_id, "org-acme")

    # Agent cannot perform employee.delete or salary view without explicit permission/capability
    assert auth_policy.can(agent_actor, HRMSAction.EMPLOYEE_DELETE, "org-acme") is False
    assert auth_policy.can(agent_actor, HRMSAction.EMPLOYEE_VIEW_SALARY, "org-acme") is False
