"""
ML Domain Exceptions — Hierarchy of predictive platform errors.
"""

from __future__ import annotations


class MLException(Exception):
    """Base exception for all ML domain errors."""

    pass


class ModelNotFoundError(MLException):
    """Raised when a requested model or version is not registered."""

    pass


class InvalidFeatureError(MLException):
    """Raised when input features fail schema, range, or null constraints."""

    pass


class InsufficientDataError(MLException):
    """Raised when required features are missing or below volume thresholds."""

    pass


class OutOfDistributionError(MLException):
    """Raised when inference input severely violates training distribution bounds."""

    pass


class ModelStageTransitionError(MLException):
    """Raised when an invalid lifecycle promotion or rollback is attempted."""

    pass


class GovernanceCheckFailedError(MLException):
    """Raised when deployment gates or fairness checks fail."""

    pass


class TenantAccessViolationError(MLException):
    """Raised when cross-tenant access to models, features, or predictions is detected."""

    pass
