"""
Governance Policy Service — Alias wrapper forwarding to PolicyService.
"""

from __future__ import annotations

from backend.agents.governance.application.policy_service import GovernancePolicyService

__all__ = ["GovernancePolicyService"]
