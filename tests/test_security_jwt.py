"""Tests — JWT issuance, claims, signature verification, and expiration."""

from datetime import timedelta

import pytest

from backend.hrms.domain.actor import ActorType
from backend.security.application.jwt import JWTInvalidTokenError, JWTService, TokenType


def test_jwt_issuance_and_decoding():
    jwt_svc = JWTService()
    tok = jwt_svc.create_access_token(
        subject="usr-001",
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
        roles={"EMPLOYEE"},
        permissions={"EMPLOYEE_READ"},
    )
    assert tok is not None

    payload = jwt_svc.decode_token(tok, expected_type=TokenType.ACCESS)
    assert payload.sub == "usr-001"
    assert payload.actor_id == "actor-001"
    assert payload.organization_id == "org-acme"
    assert payload.actor_type == ActorType.HUMAN
    assert "EMPLOYEE_READ" in payload.permissions


def test_jwt_invalid_signature_fails():
    jwt_svc = JWTService(secret_key="key-1")
    tok = jwt_svc.create_access_token(
        subject="usr-001",
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
    )

    verifier = JWTService(secret_key="key-2-wrong")
    with pytest.raises(JWTInvalidTokenError):
        verifier.decode_token(tok, expected_type=TokenType.ACCESS)


def test_jwt_expired_token_fails():
    jwt_svc = JWTService()
    tok = jwt_svc.create_access_token(
        subject="usr-001",
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
        expires_delta=timedelta(seconds=-10),  # Expired in past
    )

    with pytest.raises(JWTInvalidTokenError):
        jwt_svc.decode_token(tok, expected_type=TokenType.ACCESS)


def test_jwt_token_type_mismatch_fails():
    jwt_svc = JWTService()
    refresh_tok, _, _ = jwt_svc.create_refresh_token(
        subject="usr-001",
        actor_id="actor-001",
        organization_id="org-acme",
        actor_type=ActorType.HUMAN,
        family_id="fam-1",
    )

    # Attempting to decode refresh token as access token must fail!
    with pytest.raises(JWTInvalidTokenError, match="Token type mismatch"):
        jwt_svc.decode_token(refresh_tok, expected_type=TokenType.ACCESS)
