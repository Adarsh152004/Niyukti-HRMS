"""
Tests for Model Metrics and Probability Calibration.
"""

from __future__ import annotations

from backend.ml.evaluation.calibration import ProbabilityCalibrationEvaluator
from backend.ml.evaluation.metrics import ModelMetricsCalculator


def test_classification_and_regression_metrics():
    y_true = [1, 0, 1, 1, 0, 0, 1, 0]
    y_pred = [1, 0, 1, 0, 0, 0, 1, 1]
    y_prob = [0.9, 0.1, 0.8, 0.4, 0.2, 0.1, 0.95, 0.6]

    metrics = ModelMetricsCalculator.classification_metrics(y_true, y_pred, y_prob)
    assert metrics["accuracy"] == 0.75
    assert metrics["precision"] == 0.75
    assert "roc_auc" in metrics

    # Regression
    yt_reg = [10.0, 20.0, 30.0, 40.0]
    yp_reg = [11.0, 19.0, 32.0, 38.0]
    reg_metrics = ModelMetricsCalculator.regression_metrics(yt_reg, yp_reg)
    assert reg_metrics["mae"] == 1.5
    assert reg_metrics["rmse"] > 0


def test_probability_calibration_evaluation():
    y_true = [1, 1, 0, 0, 1, 0, 1, 0]
    y_prob = [0.85, 0.90, 0.15, 0.20, 0.80, 0.30, 0.75, 0.10]

    cal_res = ProbabilityCalibrationEvaluator.evaluate_calibration(y_true, y_prob, num_bins=5)
    assert cal_res.brier_score < 0.15
    assert cal_res.expected_calibration_error < 0.25
    assert len(cal_res.bins) > 0
