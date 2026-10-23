"""
AI Data Firewall — Prevents sensitive PII, passwords, secrets, and raw HR data leakage to external models.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Patterns for sensitive data detection
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")
API_KEY_PATTERN = re.compile(r"(?i)(api[_-]?key|secret|token|password|bearer)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


class AIDataFirewall:
    """Pre-dispatch data sanitizer filtering prompts before sending to external LLM providers."""

    @staticmethod
    def sanitize_prompt(text: str, mask_emails: bool = False) -> str:
        """
        Scan and redact high-risk PII and API keys from prompt strings.
        Ensures production secrets and government identifiers never leak to model providers.
        """
        sanitized = text

        # Redact SSNs and National IDs
        sanitized = SSN_PATTERN.sub("[REDACTED_NATIONAL_ID]", sanitized)

        # Redact Credit Cards / Bank Accounts
        sanitized = CREDIT_CARD_PATTERN.sub("[REDACTED_PAYMENT_CARD]", sanitized)

        # Redact API Keys / Passwords
        sanitized = API_KEY_PATTERN.sub(r"\1: [REDACTED_SECRET]", sanitized)

        # Optional Email Masking
        if mask_emails:
            sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)

        return sanitized

    @staticmethod
    def inspect_and_filter_payload(payload: dict[str, Any]) -> dict[str, Any]:
        """Recursively scrub sensitive keys and patterns from dictionary payloads."""
        cleaned: dict[str, Any] = {}
        for k, v in payload.items():
            k_lower = k.lower()
            if any(secret_kw in k_lower for secret_kw in ["password", "token", "secret", "api_key", "jwt", "ssn", "national_id"]):
                cleaned[k] = "[REDACTED_BY_DATA_FIREWALL]"
            elif isinstance(v, str):
                cleaned[k] = AIDataFirewall.sanitize_prompt(v)
            elif isinstance(v, dict):
                cleaned[k] = AIDataFirewall.inspect_and_filter_payload(v)
            elif isinstance(v, list):
                cleaned[k] = [AIDataFirewall.sanitize_prompt(item) if isinstance(item, str) else item for item in v]
            else:
                cleaned[k] = v
        return cleaned
