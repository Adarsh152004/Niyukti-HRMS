"""
AI-Powered Intelligent HRMS — Program 22 Predictive ML Platform Test Suite.

Verifies:
1. Continuous Calibration & Evaluation Runner
2. Expected Calibration Error (ECE) threshold <= 0.15
"""

import pytest

from backend.ml.calibration.runner import ContinuousEvaluationRunner


def test_predictive_ml_calibration_runner():
    """Verify ML model continuous evaluation runner."""
    eval_runner = ContinuousEvaluationRunner()
    report = eval_runner.run_full_suite()
    assert report.overall_status == "PASSED"
    assert report.ml_calibration.expected_calibration_error <= 0.15
