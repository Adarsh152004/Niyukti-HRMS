"""
Baseline ML Algorithms — Reference algorithms for Classification, Regression, and Ranking.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any


class BaselineClassifier:
    """
    Reference Logistic Regression / Weighted Linear Classifier.
    Computes P(Y=1) = sigmoid(w^T x + b) with feature scaling.
    """

    def __init__(self, feature_names: Sequence[str]) -> None:
        self.feature_names = list(feature_names)
        self.weights: dict[str, float] = dict.fromkeys(self.feature_names, 0.1)
        self.bias: float = 0.0

    def fit(self, train_data: Sequence[dict[str, Any]], target_column: str, epochs: int = 20, lr: float = 0.05) -> None:
        """Simple Gradient Descent optimization."""
        if not train_data:
            return

        for _ in range(epochs):
            for row in train_data:
                y = float(row.get(target_column, 0))
                # Compute prediction
                z = self.bias + sum(self.weights[f] * float(row.get(f, 0.0)) for f in self.feature_names)
                # Clip z to prevent overflow
                z_clipped = max(-15.0, min(15.0, z))
                p = 1.0 / (1.0 + math.exp(-z_clipped))

                # Gradient step
                error = p - y
                self.bias -= lr * error
                for f in self.feature_names:
                    self.weights[f] -= lr * error * float(row.get(f, 0.0))

    def predict_proba(self, features: dict[str, Any]) -> float:
        """Return calibrated probability P(Y=1)."""
        z = self.bias + sum(self.weights.get(f, 0.0) * float(features.get(f, 0.0)) for f in self.feature_names)
        z_clipped = max(-15.0, min(15.0, z))
        return round(1.0 / (1.0 + math.exp(-z_clipped)), 4)

    def predict(self, features: dict[str, Any], threshold: float = 0.50) -> int:
        return 1 if self.predict_proba(features) >= threshold else 0


class BaselineRegressor:
    """
    Reference Linear Regressor for performance/workforce projection.
    """

    def __init__(self, feature_names: Sequence[str]) -> None:
        self.feature_names = list(feature_names)
        self.weights: dict[str, float] = dict.fromkeys(self.feature_names, 0.1)
        self.bias: float = 0.0

    def fit(self, train_data: Sequence[dict[str, Any]], target_column: str, epochs: int = 20, lr: float = 0.01) -> None:
        if not train_data:
            return

        for _ in range(epochs):
            for row in train_data:
                y = float(row.get(target_column, 0.0))
                y_hat = self.bias + sum(self.weights[f] * float(row.get(f, 0.0)) for f in self.feature_names)
                error = y_hat - y
                self.bias -= lr * error
                for f in self.feature_names:
                    self.weights[f] -= lr * error * float(row.get(f, 0.0))

    def predict(self, features: dict[str, Any]) -> float:
        val = self.bias + sum(self.weights.get(f, 0.0) * float(features.get(f, 0.0)) for f in self.feature_names)
        return round(val, 2)
