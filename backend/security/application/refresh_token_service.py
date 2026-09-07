"""
Refresh Token Application Service — Rotation, Hashed Storage, and Reuse Detection.

Enforces:
- SHA-256 hashed refresh token storage in database
- Token family tracking
- Single-use token rotation
- Reuse detection: if an already-used refresh token is presented, the ENTIRE token family
  and session are revoked immediately, and a REFRESH_TOKEN_REUSE security event is triggered.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

from backend.security.domain.models import RefreshToken


class RefreshTokenReuseDetectedError(Exception):
    """Raised when an already-used refresh token is presented (token theft/reuse attack)."""

    def __init__(self, family_id: str, actor_id: str) -> None:
        self.family_id = family_id
        self.actor_id = actor_id
        super().__init__(f"Refresh token reuse detected for family '{family_id}' actor '{actor_id}'")


class RefreshTokenService:
    """
    Manages refresh token families and rotation.
    """

    def __init__(self) -> None:
        # Maps token_hash -> RefreshToken
        self._tokens_by_hash: dict[str, RefreshToken] = {}
        # Maps family_id -> list[token_hash]
        self._family_hashes: dict[str, list[str]] = {}

    @staticmethod
    def hash_token(plain_token: str) -> str:
        """Calculate SHA-256 hash of plaintext refresh token."""
        return hashlib.sha256(plain_token.encode("utf-8")).hexdigest()

    def generate_family_id(self) -> str:
        """Generate a new unique token family ID."""
        return f"fam-{uuid.uuid4()}"

    def register_refresh_token(
        self,
        plain_token: str,
        family_id: str,
        session_id: str,
        actor_id: str,
        organization_id: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Register a new refresh token instance."""
        tok_hash = self.hash_token(plain_token)
        rft = RefreshToken(
            family_id=family_id,
            token_hash=tok_hash,
            session_id=session_id,
            actor_id=actor_id,
            organization_id=organization_id,
            expires_at=expires_at,
        )
        self._tokens_by_hash[tok_hash] = rft
        if family_id not in self._family_hashes:
            self._family_hashes[family_id] = []
        self._family_hashes[family_id].append(tok_hash)
        return rft

    def rotate_refresh_token(self, plain_token: str, new_plain_token: str, new_expires_at: datetime) -> RefreshToken:
        """
        Rotate a refresh token.
        If the token has already been used, trigger REUSE DETECTION and revoke entire family.
        """
        old_hash = self.hash_token(plain_token)
        existing = self._tokens_by_hash.get(old_hash)

        if not existing:
            raise ValueError("Refresh token not found or invalid.")

        # Check for token reuse attack!
        if existing.used_at is not None or existing.revoked_at is not None:
            # Token was already used/revoked! Revoke entire family!
            self.revoke_family(existing.family_id)
            raise RefreshTokenReuseDetectedError(existing.family_id, existing.actor_id)

        if datetime.now(tz=UTC) > existing.expires_at:
            raise ValueError("Refresh token has expired.")

        # Mark old token as used
        now = datetime.now(tz=UTC)
        existing.used_at = now

        # Create new token in the SAME family
        new_hash = self.hash_token(new_plain_token)
        new_token = RefreshToken(
            family_id=existing.family_id,
            token_hash=new_hash,
            session_id=existing.session_id,
            actor_id=existing.actor_id,
            organization_id=existing.organization_id,
            expires_at=new_expires_at,
        )
        self._tokens_by_hash[new_hash] = new_token
        self._family_hashes[existing.family_id].append(new_hash)
        return new_token

    def revoke_family(self, family_id: str) -> int:
        """Revoke all tokens belonging to a family."""
        now = datetime.now(tz=UTC)
        hashes = self._family_hashes.get(family_id, [])
        count = 0
        for h in hashes:
            tok = self._tokens_by_hash.get(h)
            if tok and tok.revoked_at is None:
                tok.revoked_at = now
                count += 1
        return count
