"""Unit tests for cryptographic security utilities."""
from datetime import timedelta
import pytest
import jwt
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification():
    """Ensure Argon2id correctly hashes and verifies plaintext passwords."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2id$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_access_token_creation_and_decoding():
    """Ensure JWT access tokens encode payload and decode accurately."""
    payload = {"sub": "user_12345", "role": "user"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=5))

    decoded = decode_token(token)
    assert decoded["sub"] == "user_12345"
    assert decoded["role"] == "user"
    assert decoded["token_type"] == "access"
    assert "exp" in decoded
    assert "iat" in decoded


def test_refresh_token_creation():
    """Ensure refresh token is generated with correct token_type."""
    payload = {"sub": "user_12345"}
    token = create_refresh_token(payload, expires_delta=timedelta(days=7))

    decoded = decode_token(token)
    assert decoded["sub"] == "user_12345"
    assert decoded["token_type"] == "refresh"


def test_expired_token_raises_error():
    """Ensure expired tokens raise jwt.ExpiredSignatureError on decode."""
    payload = {"sub": "user_12345"}
    # Token expired 1 minute ago
    expired_token = create_access_token(payload, expires_delta=timedelta(minutes=-1))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(expired_token)
