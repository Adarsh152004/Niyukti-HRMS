"""Tests — API Key generation, SHA-256 hashing, scope validation, and revocation."""

import pytest

from backend.security.application.api_key_service import APIKeyService
from backend.security.domain.enums import APIKeyStatus


def test_api_key_creation_and_verification():
    svc = APIKeyService()
    key_entity, raw_secret_key = svc.create_api_key(
        organization_id="org-acme",
        owner_actor_id="actor-001",
        scopes=["employee.read", "employee.write"],
    )

    assert key_entity.key_id is not None
    assert key_entity.prefix.startswith("hrms_live")
    assert raw_secret_key.startswith(key_entity.prefix)
    # Raw secret key is NOT equal to hashed key stored in entity
    assert key_entity.key_hash != raw_secret_key

    # Verify raw secret key
    verified = svc.verify_api_key(raw_secret_key)
    assert verified.key_id == key_entity.key_id
    assert "employee.read" in verified.scopes


def test_api_key_revocation():
    svc = APIKeyService()
    key_entity, raw_secret_key = svc.create_api_key(
        organization_id="org-acme",
        owner_actor_id="actor-001",
        scopes=["employee.read"],
    )

    svc.revoke_api_key(key_entity.key_id)
    assert key_entity.status == APIKeyStatus.REVOKED
    assert key_entity.is_valid is False

    with pytest.raises(ValueError, match="invalid, expired, or revoked"):
        svc.verify_api_key(raw_secret_key)
