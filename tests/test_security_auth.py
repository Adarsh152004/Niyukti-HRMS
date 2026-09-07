"""Tests — User Authentication, Password Hashing, Policy, and Lockout."""

import contextlib

import pytest

from backend.security.application.auth_service import AuthenticationError, AuthenticationService
from backend.security.application.password import PasswordHasher, PasswordPolicyViolation, validate_password_policy
from backend.security.domain.enums import UserStatus


def test_password_hashing_and_verification():
    raw_password = "SecurePassword123!"
    hashed = PasswordHasher.hash_password(raw_password)
    assert hashed != raw_password
    assert PasswordHasher.verify_password(raw_password, hashed) is True
    assert PasswordHasher.verify_password("WrongPassword123!", hashed) is False


def test_password_policy_validation():
    # Valid password
    validate_password_policy("StrongPass123")

    # Invalid: Too short
    with pytest.raises(PasswordPolicyViolation):
        validate_password_policy("Short1")

    # Invalid: No digit
    with pytest.raises(PasswordPolicyViolation):
        validate_password_policy("NoDigitsPassword")

    # Invalid: No uppercase
    with pytest.raises(PasswordPolicyViolation):
        validate_password_policy("lowercase123")


def test_successful_user_login():
    auth_svc = AuthenticationService()
    auth_svc.register_user("org-acme", "johndoe", "john.doe@acme.com", "SecretPass123!")

    access_tok, refresh_tok, session, identity = auth_svc.authenticate_user(
        organization_id="org-acme",
        email="john.doe@acme.com",
        password="SecretPass123!",
    )
    assert access_tok is not None
    assert refresh_tok is not None
    assert session.is_active is True
    assert identity.organization_id == "org-acme"
    assert identity.actor_id is not None


def test_invalid_password_login_failure():
    auth_svc = AuthenticationService()
    auth_svc.register_user("org-acme", "johndoe", "john.doe@acme.com", "SecretPass123!")

    with pytest.raises(AuthenticationError):
        auth_svc.authenticate_user("org-acme", "john.doe@acme.com", "WrongPassword!")


def test_account_lockout_after_failed_attempts():
    auth_svc = AuthenticationService()
    user = auth_svc.register_user("org-acme", "johndoe", "john.doe@acme.com", "SecretPass123!")

    # Perform 5 failed login attempts
    for _ in range(5):
        with contextlib.suppress(AuthenticationError):
            auth_svc.authenticate_user("org-acme", "john.doe@acme.com", "WrongPass1!")

    assert user.status == UserStatus.LOCKED
    assert user.is_locked is True

    # Subsequent attempt fails due to account lockout
    with pytest.raises(AuthenticationError, match="locked"):
        auth_svc.authenticate_user("org-acme", "john.doe@acme.com", "SecretPass123!")
