"""
API Key Application Service — Generation, SHA-256 Hashing, Scope Validation, and Revocation.

Raw secret API keys are shown ONCE at creation and NEVER stored in the database.
Only the SHA-256 hash is stored.
"""

from __future__ import annotations

import hashlib
import secrets
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from backend.security.domain.enums import APIKeyStatus
from backend.security.domain.models import APIKey


class APIKeyService:
    """
    Service managing integration API Keys.
    """

    def __init__(self) -> None:
        self._keys_by_id: dict[str, APIKey] = {}
        self._keys_by_hash: dict[str, APIKey] = {}

    @staticmethod
    def hash_key(raw_key: str) -> str:
        """Calculate SHA-256 hash of raw API key."""
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def create_api_key(
        self,
        organization_id: str,
        owner_actor_id: str,
        scopes: set[str] | list[str],
        name_prefix: str = "hrms_live",
        expires_days: int | None = 365,
    ) -> tuple[APIKey, str]:
        """
        Generate a new API key.
        Returns: (APIKey_entity, raw_secret_key_string)
        """
        prefix_rand = secrets.token_hex(4)
        secret_rand = secrets.token_urlsafe(32)
        prefix = f"{name_prefix}_{prefix_rand}"
        raw_secret_key = f"{prefix}_{secret_rand}"
        key_hash = self.hash_key(raw_secret_key)

        now = datetime.now(tz=UTC)
        expires_at = now + timedelta(days=expires_days) if expires_days else None

        key_entity = APIKey(
            organization_id=organization_id,
            owner_actor_id=owner_actor_id,
            prefix=prefix,
            key_hash=key_hash,
            scopes=set(scopes),
            status=APIKeyStatus.ACTIVE,
            expires_at=expires_at,
            created_at=now,
        )

        self._keys_by_id[key_entity.key_id] = key_entity
        self._keys_by_hash[key_hash] = key_entity
        return key_entity, raw_secret_key

    def verify_api_key(self, raw_key: str) -> APIKey:
        """
        Verify raw API key string against stored hash.
        """
        key_hash = self.hash_key(raw_key)
        key_entity = self._keys_by_hash.get(key_hash)

        if not key_entity or not key_entity.is_valid:
            raise ValueError("API Key is invalid, expired, or revoked.")

        key_entity.last_used_at = datetime.now(tz=UTC)
        return key_entity

    def revoke_api_key(self, key_id: str) -> APIKey:
        """Revoke an API key."""
        key_entity = self._keys_by_id.get(key_id)
        if not key_entity:
            raise ValueError(f"API Key '{key_id}' not found.")

        now = datetime.now(tz=UTC)
        key_entity.status = APIKeyStatus.REVOKED
        key_entity.revoked_at = now
        return key_entity

    def rotate_api_key(self, key_id: str) -> tuple[APIKey, str]:
        """Revoke existing key and issue a new replacement with identical scopes."""
        old_key = self.revoke_api_key(key_id)
        return self.create_api_key(
            organization_id=old_key.organization_id,
            owner_actor_id=old_key.owner_actor_id,
            scopes=old_key.scopes,
        )

    def list_keys_for_organization(self, organization_id: str) -> Sequence[APIKey]:
        """List all API keys belonging to an organization."""
        return [k for k in self._keys_by_id.values() if k.organization_id == organization_id]
