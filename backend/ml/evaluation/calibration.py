"""
Probability Calibration Engine — Computes Brier Score, Expected Calibration Error (ECE), and Reliability Bins.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple


class CalibrationBin(NamedTuple):
    bin_lower: float
    bin_upper: float
    avg_confidence: float
    true_positive_rate: float
    sample_count: int


class CalibrationResult(NamedTuple):
    brier_score: float
    expected_calibration_error: float
    bins: list[CalibrationBin]


class ProbabilityCalibrationEvaluator:
    """Evaluates whether model confidence reflects true real-world probability."""

    @staticmethod
    def evaluate_calibration(
        y_true: Sequence[int],
        y_prob: Sequence[float],
        num_bins: int = 10,
    ) -> CalibrationResult:
        """Compute Brier Score and Expected Calibration Error (ECE)."""
        if not y_true or len(y_true) != len(y_prob):
            return CalibrationResult(brier_score=0.0, expected_calibration_error=0.0, bins=[])

        n = len(y_true)

        # 1. Brier Score = (1/N) * sum((prob - true)^2)
        brier = round(sum((p - y) ** 2 for y, p in zip(y_true, y_prob, strict=False)) / n, 4)

        # 2. Binned ECE
        bin_width = 1.0 / num_bins
        bins: list[CalibrationBin] = []
        ece = 0.0

        for i in range(num_bins):
            lower = i * bin_width
            upper = (i + 1) * bin_width

            bin_indices = [
                idx for idx, p in enumerate(y_prob) if (lower <= p < upper) or (i == num_bins - 1 and lower <= p <= upper)
            ]
            count = len(bin_indices)

            if count > 0:
                avg_conf = sum(y_prob[idx] for idx in bin_indices) / count
                acc = sum(y_true[idx] for idx in bin_indices) / count
                ece += (count / n) * abs(acc - avg_conf)

                bins.append(
                    CalibrationBin(
                        bin_lower=round(lower, 2),
                        bin_upper=round(upper, 2),
                        avg_confidence=round(avg_conf, 4),
                        true_positive_rate=round(acc, 4),
                        sample_count=count,
                    )
                )

        return CalibrationResult(
            brier_score=brier,
            expected_calibration_error=round(ece, 4),
            bins=bins,
        )
