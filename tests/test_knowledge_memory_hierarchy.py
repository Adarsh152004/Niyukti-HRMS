"""
Tests for Memory Hierarchy (Agent, Team, Organization, Employee tiers).
"""

from __future__ import annotations

import pytest

from backend.agents.memory.domain.enums import MemoryType
from backend.agents.memory.hierarchy.enums import MemoryTier
from backend.agents.memory.hierarchy.service import HierarchicalMemoryService


@pytest.mark.asyncio
async def test_hierarchical_memory_partitions():
    mem_svc = HierarchicalMemoryService.get_instance()
    await mem_svc.clear()

    org_id = "org-mem-test"

    # 1. Agent Memory (Private to recruitment agent)
    agent_mem = await mem_svc.write_memory(
        organization_id=org_id,
        tier=MemoryTier.AGENT,
        content="Candidate #104 demonstrated strong Python and FastAPI skills during screening.",
        memory_type=MemoryType.OBSERVATION,
        agent_id="agent-recruiter-1",
    )
    assert agent_mem.tier == MemoryTier.AGENT

    # 2. Team Memory (Shared across Recruitment squad)
    team_mem = await mem_svc.write_memory(
        organization_id=org_id,
        tier=MemoryTier.TEAM,
        content="Recruitment target for Q3: 15 Senior Backend Engineers.",
        memory_type=MemoryType.FACT,
        team_id="squad-recruitment",
    )
    assert team_mem.tier == MemoryTier.TEAM

    # 3. Organization Memory (Company-wide)
    org_mem = await mem_svc.write_memory(
        organization_id=org_id,
        tier=MemoryTier.ORGANIZATION,
        content="Core office core hours: 10 AM to 4 PM IST.",
        memory_type=MemoryType.FACT,
    )
    assert org_mem.tier == MemoryTier.ORGANIZATION

    # 4. Employee Memory (Private to employee)
    emp_mem = await mem_svc.write_memory(
        organization_id=org_id,
        tier=MemoryTier.EMPLOYEE,
        content="Employee preferred working schedule is Monday-Wednesday in office.",
        memory_type=MemoryType.CONVERSATION,
        employee_id="emp-alice-101",
    )
    assert emp_mem.tier == MemoryTier.EMPLOYEE

    # ── Verify Access Control Boundaries ──

    # Recruiter 1 reads AGENT memory -> CAN see own memory
    res_agent1 = await mem_svc.read_memories(
        organization_id=org_id,
        tier=MemoryTier.AGENT,
        requesting_actor_id="user-recruiter-1",
        requesting_agent_id="agent-recruiter-1",
    )
    assert len(res_agent1) == 1
    assert res_agent1[0].memory_id == agent_mem.memory_id

    # Recruiter 2 reads AGENT memory -> CANNOT see Recruiter 1's private memory
    res_agent2 = await mem_svc.read_memories(
        organization_id=org_id,
        tier=MemoryTier.AGENT,
        requesting_actor_id="user-recruiter-2",
        requesting_agent_id="agent-recruiter-2",
    )
    assert len(res_agent2) == 0

    # Team member of squad-recruitment reads TEAM memory -> CAN see team memory
    res_team = await mem_svc.read_memories(
        organization_id=org_id,
        tier=MemoryTier.TEAM,
        requesting_actor_id="user-recruiter-2",
        agent_teams=["squad-recruitment"],
    )
    assert len(res_team) == 1
    assert res_team[0].memory_id == team_mem.memory_id

    # Non-team member reads TEAM memory -> CANNOT see recruitment squad memory
    res_team_unauth = await mem_svc.read_memories(
        organization_id=org_id,
        tier=MemoryTier.TEAM,
        requesting_actor_id="user-payroll-1",
        agent_teams=["squad-payroll"],
    )
    assert len(res_team_unauth) == 0

    # Employee Alice reads own EMPLOYEE memory -> CAN see
    res_emp = await mem_svc.read_memories(
        organization_id=org_id,
        tier=MemoryTier.EMPLOYEE,
        requesting_actor_id="emp-alice-101",
        employee_id="emp-alice-101",
    )
    assert len(res_emp) == 1

    # Another employee Bob reads Alice's EMPLOYEE memory -> CANNOT see
    res_emp_bob = await mem_svc.read_memories(
        organization_id=org_id,
        tier=MemoryTier.EMPLOYEE,
        requesting_actor_id="emp-bob-202",
        employee_id="emp-alice-101",
    )
    assert len(res_emp_bob) == 0
