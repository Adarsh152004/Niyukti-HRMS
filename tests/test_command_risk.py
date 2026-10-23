"""Tests — Risk Engine classification (LOW, MEDIUM, HIGH, CRITICAL)."""

from backend.commands.application.risk_engine import RiskEngine
from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import Command


def test_risk_classification_heuristics():
    engine = RiskEngine()

    # Read operation -> LOW
    cmd_read = Command(command_type="employee.read", actor_id="a1", organization_id="o1")
    assert engine.assess_risk(cmd_read).risk_level == RiskLevel.LOW

    # Create operation -> MEDIUM
    cmd_create = Command(command_type="employee.create", actor_id="a1", organization_id="o1")
    assert engine.assess_risk(cmd_create).risk_level == RiskLevel.MEDIUM

    # Terminate operation -> HIGH
    cmd_term = Command(command_type="employee.terminate", actor_id="a1", organization_id="o1")
    assert engine.assess_risk(cmd_term).risk_level == RiskLevel.HIGH

    # Delete org -> CRITICAL
    cmd_crit = Command(command_type="organization.delete_organization", actor_id="a1", organization_id="o1")
    assert engine.assess_risk(cmd_crit).risk_level == RiskLevel.CRITICAL


def test_risk_override_mapping():
    engine = RiskEngine()
    engine.set_risk_override("custom.action", RiskLevel.CRITICAL)

    cmd = Command(command_type="custom.action", actor_id="a1", organization_id="o1")
    res = engine.assess_risk(cmd)
    assert res.risk_level == RiskLevel.CRITICAL
    assert res.score == 4
