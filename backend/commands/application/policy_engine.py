"""
Policy Engine — Dynamic evaluation of policy conditions independent of authorization.

Answers: "Under what conditions is this command allowed?"
"""

from __future__ import annotations

from collections.abc import Callable

from backend.commands.domain.enums import PolicyDecision, RiskLevel
from backend.commands.domain.models import Command, CommandContext, PolicyContext, PolicyDecisionResult, PolicyRule
from backend.hrms.domain.actor import ActorType


class PolicyEngine:
    """
    Policy evaluation engine.
    Evaluates system invariants and domain policy rules.
    """

    def __init__(self) -> None:
        self._rules: list[tuple[PolicyRule, Callable[[PolicyContext], bool]]] = []
        self._register_default_rules()

    def add_rule(self, rule: PolicyRule, condition_fn: Callable[[PolicyContext], bool]) -> None:
        """Register a custom policy rule and boolean condition checker."""
        self._rules.append((rule, condition_fn))

    def evaluate(self, command: Command, context: CommandContext, risk_level: RiskLevel = RiskLevel.LOW) -> PolicyDecisionResult:
        """
        Evaluate all policy rules against the given command context and risk level.
        Returns: PolicyDecisionResult (ALLOW, DENY, or REQUIRE_APPROVAL)
        """
        policy_ctx = PolicyContext(command=command, context=context)

        # 1. Evaluate registered policy rules
        for rule, condition_fn in self._rules:
            if condition_fn(policy_ctx):
                return PolicyDecisionResult(
                    decision=rule.decision_if_matched,
                    rule_id=rule.rule_id,
                    reason=f"Policy rule '{rule.name}' matched: {rule.reason}",
                )

        # 2. Risk-based policy rule fallback
        if risk_level >= RiskLevel.HIGH:
            return PolicyDecisionResult(
                decision=PolicyDecision.REQUIRE_APPROVAL,
                rule_id="RULE-RISK-HIGH-HITL",
                reason=f"Action classified as '{risk_level.value}' risk requires Human-In-The-Loop approval.",
            )

        return PolicyDecisionResult(
            decision=PolicyDecision.ALLOW,
            rule_id=None,
            reason="All policy checks passed.",
        )

    def _register_default_rules(self) -> None:
        """Register default system policy rules."""
        # Rule: AI Agent cannot terminate employees directly
        self.add_rule(
            PolicyRule(
                rule_id="RULE-AGENT-NO-TERMINATE",
                name="Block AI Agent Termination",
                description="AI Agents cannot terminate employees directly",
                decision_if_matched=PolicyDecision.REQUIRE_APPROVAL,
                reason="Employee termination by AI Agent requires human confirmation",
            ),
            lambda ctx: (
                ctx.context.actor.actor_type == ActorType.AI_AGENT and ctx.command.command_type.lower().endswith("terminate")
            ),
        )

        # Rule: AI Agent cannot modify security roles
        self.add_rule(
            PolicyRule(
                rule_id="RULE-AGENT-NO-ROLE-CHANGE",
                name="Block AI Agent Role Modification",
                description="AI Agents cannot assign or modify security roles",
                decision_if_matched=PolicyDecision.DENY,
                reason="AI Agents are prohibited from altering security roles",
            ),
            lambda ctx: (ctx.context.actor.actor_type == ActorType.AI_AGENT and "role" in ctx.command.command_type.lower()),
        )
