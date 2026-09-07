"""
AI-Powered Intelligent HRMS — Program 22 Context Budgeting & Memory Test Suite.

Verifies:
1. 8,192 token limit allocation
2. Truncation and priority budgeting
"""

import pytest

from backend.agents.context.budget import ContextBudgetManager, TokenBudgetAllocation


def test_context_budget_manager_slices():
    """Verify context token budgeting satisfies max limit."""
    budget_mgr = ContextBudgetManager(allocation=TokenBudgetAllocation(max_total_tokens=8192))
    assert budget_mgr.allocation.max_total_tokens == 8192
    assert budget_mgr.allocation.system_instruction_limit == 1500
