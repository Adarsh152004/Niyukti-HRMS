"""
Tests for Idempotent Agent Bootstrapping and Tenant Isolation.
"""

from __future__ import annotations

from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.domain.enums import SpecializedAgentRole


def test_idempotent_bootstrap_and_tenant_isolation():
    svc = SpecializedAgentService.get_instance()
    org_a = "org-boot-alpha"
    org_b = "org-boot-beta"

    # 1. First bootstrap: 24 created
    res_1 = svc.bootstrap_tenant(org_a)
    assert res_1.created_count == 24
    assert res_1.updated_count == 0
    assert res_1.skipped_count == 0
    assert len(res_1.instances) == 24

    # 2. Second bootstrap: 0 created, 24 skipped (Idempotent)
    res_2 = svc.bootstrap_tenant(org_a)
    assert res_2.created_count == 0
    assert res_2.updated_count == 0
    assert res_2.skipped_count == 24
    assert len(res_2.instances) == 24

    # 3. Bootstrap Org B independently
    res_b = svc.bootstrap_tenant(org_b)
    assert res_b.created_count == 24

    # 4. Verify tenant isolation in instances
    inst_a = svc.get_tenant_instance(org_a, SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT)
    inst_b = svc.get_tenant_instance(org_b, SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT)

    assert inst_a.organization_id == org_a
    assert inst_b.organization_id == org_b
    assert inst_a.instance_id != inst_b.instance_id
    assert inst_a.agent_id != inst_b.agent_id
