"""
Model Drift Monitoring — Statistical shift detection in feature distributions and missingness rates.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.ml.domain.enums import DriftSeverity
from backend.ml.domain.models import DriftReport


class DriftDetector:
    """Computes distribution shift and missingness rate degradation between training baseline and inference traffic."""

    @staticmethod
    def evaluate_numeric_drift(
        organization_id: str,
        model_id: str,
        model_version_id: str,
        feature_name: str,
        baseline_values: Sequence[float],
        current_values: Sequence[float],
        baseline_missing_count: int = 0,
        current_missing_count: int = 0,
    ) -> DriftReport:
        """
        Evaluate drift via normalized mean difference and missingness shift:
        Drift Score = |Mean(Current) - Mean(Baseline)| / StdDev(Baseline)
        """
        b_count = max(1, len(baseline_values) + baseline_missing_count)
        c_count = max(1, len(current_values) + current_missing_count)

        b_miss_rate = baseline_missing_count / b_count
        c_miss_rate = current_missing_count / c_count

        b_mean = sum(baseline_values) / max(1, len(baseline_values)) if baseline_values else 0.0
        c_mean = sum(current_values) / max(1, len(current_values)) if current_values else 0.0

        # Compute baseline variance
        variance = (
            sum((v - b_mean) ** 2 for v in baseline_values) / max(1, len(baseline_values)) if len(baseline_values) > 1 else 1.0
        )
        std_dev = max(0.001, variance**0.5)

        # Drift score in standard deviations
        drift_score = round(abs(c_mean - b_mean) / std_dev, 4)

        # Classify severity
        if drift_score < 0.20 and abs(c_miss_rate - b_miss_rate) < 0.05:
            severity = DriftSeverity.NONE
        elif drift_score < 0.50:
            severity = DriftSeverity.LOW
        elif drift_score < 1.00:
            severity = DriftSeverity.MEDIUM
        elif drift_score < 2.00:
            severity = DriftSeverity.HIGH
        else:
            severity = DriftSeverity.CRITICAL

        return DriftReport(
            organization_id=organization_id,
            model_id=model_id,
            model_version_id=model_version_id,
            feature_name=feature_name,
            drift_score=drift_score,
            severity=severity,
            baseline_mean=round(b_mean, 4),
            current_mean=round(c_mean, 4),
            baseline_missing_rate=round(b_miss_rate, 4),
            current_missing_rate=round(c_miss_rate, 4),
        )
