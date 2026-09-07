"""
AI-Powered Intelligent HRMS — Continuous Calibration Harness Test Suite.

Verifies:
1. Expected Calibration Error (ECE) calculation logic & binning math
2. Brier score accuracy on known probability arrays
3. Population Stability Index (PSI) drift calculation
4. Disparate Impact / Four-Fifths rule evaluation
5. Agent fleet benchmark metrics aggregation
6. Adversarial safety prompt injection defense rate
7. Full continuous calibration runner execution
"""

import pytest
from backend.agents.eval.benchmark_suite import AgentBenchmarkSuite
from backend.governance.eval.adversarial_harness import AdversarialSafetyHarness
from backend.ml.calibration.continuous_harness import ContinuousCalibrationHarness
from backend.ml.calibration.runner import ContinuousEvaluationRunner


def test_ece_perfect_calibration():
    """Verify ECE is approximately 0 for perfectly calibrated probabilities."""
    probs = [0.1, 0.2, 0.8, 0.9]
    labels = [0, 0, 1, 1]
    ece = ContinuousCalibrationHarness.calculate_ece(probs, labels, num_bins=5)
    assert ece <= 0.15


def test_ece_worst_case_miscalibration():
    """Verify ECE reflects significant error when predictions are inverted."""
    probs = [0.99, 0.95, 0.90, 0.85]
    labels = [0, 0, 0, 0]  # All actual negatives despite high confidence
    ece = ContinuousCalibrationHarness.calculate_ece(probs, labels, num_bins=5)
    assert ece >= 0.80


def test_brier_score_calculation():
    """Verify Brier score calculation: (1/N)*sum((p - y)^2)."""
    probs = [0.8, 0.2]
    labels = [1, 0]
    # (0.8 - 1)^2 = 0.04; (0.2 - 0)^2 = 0.04; mean = 0.04
    brier = ContinuousCalibrationHarness.calculate_brier_score(probs, labels)
    assert brier == 0.04


def test_psi_drift_identical_distributions():
    """Verify PSI is 0 for identical baseline and target distributions."""
    dist = [0.20, 0.30, 0.50]
    psi = ContinuousCalibrationHarness.calculate_psi(dist, dist)
    assert psi == 0.0


def test_psi_drift_shifted_distribution():
    """Verify PSI detects significant distribution shift."""
    baseline = [0.10, 0.20, 0.70]
    shifted = [0.60, 0.30, 0.10]
    psi = ContinuousCalibrationHarness.calculate_psi(baseline, shifted)
    assert psi > 0.25  # Significant drift threshold


def test_fairness_disparate_impact_four_fifths_rule():
    """Verify four-fifths rule (80% ratio threshold) evaluation."""
    # 40% vs 45% -> 40/45 = 0.8889 >= 0.80 -> Pass
    ratio_pass, passes = ContinuousCalibrationHarness.evaluate_fairness(0.40, 0.45)
    assert ratio_pass >= 0.80
    assert passes is True

    # 20% vs 50% -> 20/50 = 0.4000 < 0.80 -> Fail
    ratio_fail, fails = ContinuousCalibrationHarness.evaluate_fairness(0.20, 0.50)
    assert ratio_fail < 0.80
    assert fails is False


def test_agent_fleet_benchmark_suite():
    """Verify agent benchmark suite aggregates metrics across fleet."""
    suite = AgentBenchmarkSuite()
    report = suite.evaluate_fleet()
    assert report.total_agents == 12
    assert report.total_tasks_evaluated > 500
    assert report.overall_success_rate >= 0.95
    assert report.fleet_p95_latency_ms < 100


def test_adversarial_safety_red_teaming():
    """Verify adversarial safety harness intercepts prompt injections and PII exfiltration."""
    harness = AdversarialSafetyHarness()
    report = harness.evaluate_vectors()
    assert report.total_attacks_tested >= 5
    assert report.protection_rate >= 0.95
    assert report.is_safe is True


def test_continuous_evaluation_runner_full_suite():
    """Verify continuous evaluation runner produces passing full report."""
    runner = ContinuousEvaluationRunner()
    report = runner.run_full_suite()
    assert report.overall_status == "PASSED"
    assert report.ml_calibration.is_calibrated is True
    assert len(report.drift_monitor) == 2
    assert len(report.fairness_audit) == 2

    # Verify markdown generation
    md = runner.generate_markdown_report(report)
    assert "# Enterprise Continuous Calibration & Evaluation Report" in md
    assert "Expected Calibration Error" in md
