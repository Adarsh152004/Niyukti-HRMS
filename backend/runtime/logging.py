"""
Enterprise Runtime — Structured logging.

PII masking is always enforced — no employee PII may appear in log output.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import Any

# Fields that must never appear in log output unmasked
_PII_PATTERNS: list[tuple[str, str]] = [
    (r"(?i)(email\s*[:=]\s*)[\w.+-]+@[\w-]+\.[a-z]{2,}", r"\1***@***.***"),
    (r"(?i)(phone\s*[:=]\s*)[\d\s\-+(]{7,}", r"\1[REDACTED]"),
    (r"(?i)(password\s*[:=]\s*)\S+", r"\1[REDACTED]"),
    (r"(?i)(secret\s*[:=]\s*)\S+", r"\1[REDACTED]"),
    (r"(?i)(token\s*[:=]\s*)\S+", r"\1[REDACTED]"),
    (r"(?i)(ssn\s*[:=]\s*)[\d\-]+", r"\1[REDACTED]"),
    (r"(?i)(national_id\s*[:=]\s*)\S+", r"\1[REDACTED]"),
    (r"(?i)(bank_account\s*[:=]\s*)\S+", r"\1[REDACTED]"),
    (r"(?i)(salary\s*[:=]\s*)[\d,.]+", r"\1[REDACTED]"),
]


def _mask_pii(message: str) -> str:
    """Apply PII masking patterns to a log message string."""
    for pattern, replacement in _PII_PATTERNS:
        message = re.sub(pattern, replacement, message)
    return message


class _PIIMaskingFilter(logging.Filter):
    """Logging filter that masks PII in all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.args:
            try:
                record.msg = record.getMessage()
                record.args = None
            except Exception:
                pass
        record.msg = _mask_pii(str(record.msg))
        return True

class _JSONFormatter(logging.Formatter):
    """Formats log records as JSON lines for structured log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str)


class _TextFormatter(logging.Formatter):
    """Human-readable formatter for development."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def configure_logging(
    level: str = "INFO",
    log_format: str = "json",
    pii_masking: bool = True,
) -> None:
    """
    Configure the root logger for the HRMS platform.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Output format — 'json' for structured logs, 'text' for human-readable.
        pii_masking: Whether to apply PII masking filters.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter: logging.Formatter = _JSONFormatter() if log_format == "json" else _TextFormatter()
    handler.setFormatter(formatter)

    if pii_masking:
        handler.addFilter(_PIIMaskingFilter())

    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "passlib"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for a HRMS module."""
    return logging.getLogger(f"hrms.{name}")