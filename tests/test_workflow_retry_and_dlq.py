"""Tests — Retry Engine exponential backoff, error classification, and Dead Letter Queue."""

from backend.workflows.application.retry_service import RetryService
from backend.workflows.domain.enums import ErrorCategory, RetryStrategy


def test_retry_error_classification():
    service = RetryService()

    # Authorization errors are NON-RETRYABLE
    assert service.classify_error("Actor is unauthorized") == ErrorCategory.AUTHORIZATION
    assert service.is_retryable("Actor is unauthorized", attempt=1, max_attempts=3) is False

    # Validation errors are NON-RETRYABLE
    assert service.classify_error("Validation error: Invalid input") == ErrorCategory.VALIDATION
    assert service.is_retryable("Validation error: Invalid input", attempt=1, max_attempts=3) is False

    # Infrastructure/Network errors are RETRYABLE
    assert service.classify_error("Database connection lost") == ErrorCategory.RETRYABLE
    assert service.is_retryable("Database connection lost", attempt=1, max_attempts=3) is True


def test_exponential_backoff_calculation():
    service = RetryService()
    policy = {
        "strategy": RetryStrategy.EXPONENTIAL.value,
        "initial_interval_seconds": 2.0,
        "backoff_multiplier": 2.0,
        "jitter": False,
    }

    t1 = service.calculate_next_retry(attempt=1, retry_policy=policy)
    t2 = service.calculate_next_retry(attempt=2, retry_policy=policy)

    assert t2 > t1
