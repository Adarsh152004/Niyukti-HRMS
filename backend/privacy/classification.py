"""
PII Classification & Sensitive Field Protection.
"""

from __future__ import annotations

import base64
import hashlib
import logging
from typing import Any

from backend.security.pii import PIIClassification

logger = logging.getLogger(__name__)

# Field-level sensitivity mappings
SENSITIVE_FIELDS_MAP: dict[str, PIIClassification] = {
    "national_id": PIIClassification.RESTRICTED,
    "tax_id": PIIClassification.RESTRICTED,
    "bank_account_number": PIIClassification.RESTRICTED,
    "routing_number": PIIClassification.RESTRICTED,
    "passport_number": PIIClassification.RESTRICTED,
    "basic_salary": PIIClassification.HIGHLY_SENSITIVE,
    "bonus": PIIClassification.HIGHLY_SENSITIVE,
    "medical_conditions": PIIClassification.HIGHLY_SENSITIVE,
    "personal_email": PIIClassification.CONFIDENTIAL,
    "phone_number": PIIClassification.CONFIDENTIAL,
    "emergency_contact": PIIClassification.CONFIDENTIAL,
    "home_address": PIIClassification.CONFIDENTIAL,
}


def mask_sensitive_value(value: Any, classification: PIIClassification) -> str:
    """Mask a sensitive value based on its classification level."""
    val_str = str(value)
    if not val_str:
        return ""

    if classification == PIIClassification.HIGHLY_SENSITIVE:
        return "***REDACTED***"
    elif classification == PIIClassification.SENSITIVE:
        return f"***{val_str[-4:]}" if len(val_str) > 4 else "***"
    elif classification == PIIClassification.CONFIDENTIAL:
        if "@" in val_str:  # Email
            parts = val_str.split("@")
            return f"{parts[0][:2]}***@{parts[1]}"
        return f"{val_str[:2]}***{val_str[-2:]}" if len(val_str) > 4 else "***"
    return val_str


def deterministic_field_encrypt(value: str, secret_key: str = "hrms-default-field-key") -> str:
    """
    Encrypt sensitive field at rest (deterministic pseudo-encryption for demonstration).
    """
    key_hash = hashlib.sha256(secret_key.encode()).digest()
    raw = value.encode("utf-8")
    xor_bytes = bytes([b ^ key_hash[i % len(key_hash)] for i, b in enumerate(raw)])
    return "enc::" + base64.b64encode(xor_bytes).decode("ascii")


def deterministic_field_decrypt(encrypted: str, secret_key: str = "hrms-default-field-key") -> str:
    """Decrypt deterministic field."""
    if not encrypted.startswith("enc::"):
        return encrypted
    raw_b64 = encrypted[5:]
    xor_bytes = base64.b64decode(raw_b64.encode("ascii"))
    key_hash = hashlib.sha256(secret_key.encode()).digest()
    orig = bytes([b ^ key_hash[i % len(key_hash)] for i, b in enumerate(xor_bytes)])
    return orig.decode("utf-8")
