"""
Retry Service — Configurable Exponential Backoff with Jitter and Error Classification.

Enforces:
- Authorization and Validation errors MUST NOT be blindly retried (classified as NON_RETRYABLE).
- Calculates backoff interval with optional random jitter.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from typing import Any

from backend.workflows.domain.enums import ErrorCategory, RetryStrategy


class RetryService:
    """
    Retry Policy Calculator and Error Classifier.
    """

    @staticmethod
    def classify_error(error: Exception | str) -> ErrorCategory:
        """Classify error into retryable vs non-retryable categories."""
        err_msg = str(error).lower()

        if any(term in err_msg for term in ["unauthorized", "permission", "forbidden"]):
            return ErrorCategory.AUTHORIZATION
        if any(term in err_msg for term in ["validation", "invalid", "malformed"]):
            return ErrorCategory.VALIDATION
        if any(term in err_msg for term in ["timeout", "timed out"]):
            return ErrorCategory.TIMEOUT
        if any(term in err_msg for term in ["rate limit", "too many requests"]):
            return ErrorCategory.RATE_LIMITED

        return ErrorCategory.RETRYABLE

    def is_retryable(self, error: Exception | str, attempt: int, max_attempts: int) -> bool:
        """Check if an attempt is eligible for retry."""
        if attempt >= max_attempts:
            return False

        category = self.classify_error(error)
        return category not in (ErrorCategory.AUTHORIZATION, ErrorCategory.VALIDATION, ErrorCategory.NON_RETRYABLE)

    def calculate_next_retry(
        self,
        attempt: int,
        retry_policy: dict[str, Any],
    ) -> datetime:
        """
        Calculate next retry timestamp using configured strategy (FIXED, EXPONENTIAL, EXPONENTIAL_JITTER).
        """
        strategy = RetryStrategy(retry_policy.get("strategy", RetryStrategy.EXPONENTIAL.value))
        initial_seconds = float(retry_policy.get("initial_interval_seconds", 2.0))
        max_seconds = float(retry_policy.get("max_interval_seconds", 60.0))
        multiplier = float(retry_policy.get("backoff_multiplier", 2.0))
        use_jitter = bool(retry_policy.get("jitter", True))

        if strategy == RetryStrategy.FIXED:
            delay_seconds = initial_seconds
        elif strategy in (RetryStrategy.EXPONENTIAL, RetryStrategy.EXPONENTIAL_JITTER):
            delay_seconds = min(initial_seconds * (multiplier ** (attempt - 1)), max_seconds)
            if use_jitter or strategy == RetryStrategy.EXPONENTIAL_JITTER:
                delay_seconds = delay_seconds * random.uniform(0.8, 1.2)

        return datetime.now(tz=UTC) + timedelta(seconds=delay_seconds)
