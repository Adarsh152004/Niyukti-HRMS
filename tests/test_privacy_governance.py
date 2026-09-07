"""
Tests for HR Privacy, Consent, Retention, and DSAR Compliance.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from backend.privacy.classification import (
    deterministic_field_decrypt,
    deterministic_field_encrypt,
    mask_sensitive_value,
)
from backend.privacy.consent import ConsentPurpose, ConsentService
from backend.privacy.dsar import DSARService, DSARStatus, DSARType
from backend.privacy.retention import (
    ArchivalStatus,
    DataRetentionEngine,
    RetentionCategory,
)
from backend.security.pii import PIIClassification


def test_pii_masking_and_field_encryption():
    # Masking tests
    assert mask_sensitive_value("123-45-6789", PIIClassification.HIGHLY_SENSITIVE) == "***REDACTED***"
    assert mask_sensitive_value("95000", PIIClassification.SENSITIVE) == "***5000"
    assert mask_sensitive_value("john.doe@company.com", PIIClassification.CONFIDENTIAL) == "jo***@company.com"

    # Encryption / Decryption at rest
    raw_secret = "sensitive-bank-account-98765"
    enc = deterministic_field_encrypt(raw_secret)
    assert enc.startswith("enc::")
    assert enc != raw_secret
    dec = deterministic_field_decrypt(enc)
    assert dec == raw_secret


@pytest.mark.asyncio
async def test_consent_and_preferences():
    consent_svc = ConsentService.get_instance()
    org_id = "org-privacy-1"
    emp_id = "emp-001"

    # Check initially no consent
    has_cst = await consent_svc.has_consent(org_id, emp_id, ConsentPurpose.AI_CAREER_RECOMMENDATION)
    assert has_cst is False

    # Grant consent
    await consent_svc.record_consent(
        organization_id=org_id,
        employee_id=emp_id,
        purpose=ConsentPurpose.AI_CAREER_RECOMMENDATION,
        granted=True,
    )
    assert await consent_svc.has_consent(org_id, emp_id, ConsentPurpose.AI_CAREER_RECOMMENDATION) is True

    # Update preferences
    pref = await consent_svc.update_preferences(
        organization_id=org_id,
        employee_id=emp_id,
        preferred_channels=["EMAIL", "WHATSAPP"],
        ai_assistance_enabled=True,
    )
    assert "WHATSAPP" in pref.preferred_channels


@pytest.mark.asyncio
async def test_retention_and_legal_hold():
    engine = DataRetentionEngine.get_instance()
    org_id = "org-privacy-1"
    res_id = "candidate-cv-101"

    # Register candidate resume (180 days retention, 90 days archive)
    record = await engine.register_record(org_id, RetentionCategory.CANDIDATE_RESUME, res_id)
    assert record.status == ArchivalStatus.ACTIVE

    # Apply Legal Hold
    await engine.apply_legal_hold(org_id, RetentionCategory.CANDIDATE_RESUME, res_id, reason="Pending litigation inquiry")
    record_hold = engine._records[record.record_id]
    assert record_hold.status == ArchivalStatus.LEGAL_HOLD

    # Simulate aging
    record_hold.created_at = datetime.now(tz=UTC) - timedelta(days=200)

    # Evaluate lifecycle -> legal hold prevents purge/archive
    updated = await engine.evaluate_retention_lifecycle(org_id)
    assert not any(r.resource_id == res_id for r in updated)
    assert record_hold.status == ArchivalStatus.LEGAL_HOLD

    # Release hold
    await engine.release_legal_hold(org_id, RetentionCategory.CANDIDATE_RESUME, res_id)
    assert engine._records[record.record_id].status == ArchivalStatus.ACTIVE


@pytest.mark.asyncio
async def test_dsar_workflows():
    dsar_svc = DSARService.get_instance()
    org_id = "org-privacy-1"
    emp_id = "emp-002"

    # Employee submits DSAR export request
    req = await dsar_svc.create_request(org_id, emp_id, DSARType.ACCESS_EXPORT, details="Export all personal records")
    assert req.status == DSARStatus.SUBMITTED

    # DPO reviews and approves
    reviewed = await dsar_svc.review_request(req.request_id, reviewer_id="dpo-admin", approved=True, notes="Verified identity")
    assert reviewed.status == DSARStatus.APPROVED

    # Complete request
    completed = await dsar_svc.complete_request(req.request_id)
    assert completed.status == DSARStatus.COMPLETED
    assert completed.completed_at is not None
