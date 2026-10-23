"""
Password Security Application Service.

Handles secure password hashing using pbkdf2_sha256/bcrypt via passlib,
and validates password complexity and lockout policies.
"""

from __future__ import annotations

import re

from passlib.context import CryptContext

# Password hashing context using secure PBKDF2-SHA256 and bcrypt
_pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


class PasswordHasher:
    """
    Service for hashing and verifying passwords.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password using secure PBKDF2/bcrypt."""
        return _pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against its stored hash."""
        return _pwd_context.verify(plain_password, hashed_password)


class PasswordPolicyViolation(Exception):
    """Raised when a candidate password violates policy settings."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def validate_password_policy(
    password: str,
    min_length: int = 8,
    require_digits: bool = True,
    require_uppercase: bool = True,
    require_special: bool = False,
) -> None:
    """
    Validate candidate password against security policy rules.
    """
    if len(password) < min_length:
        raise PasswordPolicyViolation(f"Password must be at least {min_length} characters long.")

    if require_digits and not re.search(r"\d", password):
        raise PasswordPolicyViolation("Password must contain at least one digit (0-9).")

    if require_uppercase and not re.search(r"[A-Z]", password):
        raise PasswordPolicyViolation("Password must contain at least one uppercase letter.")

    if require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise PasswordPolicyViolation("Password must contain at least one special character.")
