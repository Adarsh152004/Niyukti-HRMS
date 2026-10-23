"""
Synthetic HR Dataset Generator — Generates safe, zero-PII, mathematically coherent synthetic HR records for testing.
"""

from __future__ import annotations

import random
from typing import Any


class SyntheticHRDataGenerator:
    """Generates deterministic synthetic HR tabular data for training and evaluating models."""

    @staticmethod
    def generate_attrition_dataset(
        num_records: int = 200,
        seed: int = 42,
    ) -> list[dict[str, Any]]:
        """
        Generate synthetic records with explicit ground-truth attrition labels.
        Features:
        - employee_tenure_months (0 - 120)
        - leave_frequency_90d (0 - 20)
        - attendance_rate_30d (0.60 - 1.0)
        - performance_trend_score (1.0 - 5.0)
        - salary_growth_ratio_2y (0.0 - 0.50)
        - engagement_score (10.0 - 100.0)
        - promotion_count (0 - 5)
        - gender (for post-hoc fairness evaluation: "F", "M")
        - target: will_attrite (0 or 1)
        """
        rng = random.Random(seed)
        records: list[dict[str, Any]] = []

        for i in range(num_records):
            tenure = rng.randint(6, 96)
            leave_freq = rng.randint(0, 15)
            attendance = round(rng.uniform(0.75, 1.0), 3)
            perf = round(rng.uniform(2.0, 5.0), 2)
            salary_growth = round(rng.uniform(0.0, 0.30), 3)
            engagement = round(rng.uniform(25.0, 95.0), 1)
            promotions = rng.randint(0, 3)
            gender = "F" if rng.random() > 0.50 else "M"

            # Synthetic risk formula
            risk_score = (
                (100.0 - engagement) * 0.40
                + (leave_freq * 3.0)
                + ((1.0 - attendance) * 50.0)
                - (salary_growth * 40.0)
                - (promotions * 10.0)
            )

            will_attrite = 1 if risk_score > 45.0 else 0

            records.append(
                {
                    "employee_id": f"syn-emp-{i + 1:04d}",
                    "employee_tenure_months": tenure,
                    "leave_frequency_90d": leave_freq,
                    "attendance_rate_30d": attendance,
                    "performance_trend_score": perf,
                    "salary_growth_ratio_2y": salary_growth,
                    "engagement_score": engagement,
                    "promotion_count": promotions,
                    "gender": gender,
                    "will_attrite": will_attrite,
                    "synthetic": True,
                }
            )

        return records
