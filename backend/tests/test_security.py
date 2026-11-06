from app.core.security import (
    create_access_token, create_purpose_token, decode_access_token, decode_purpose_token,
    decrypt_secret, encrypt_secret, hash_password, verify_password,
)


def test_hash_is_not_plaintext():
    assert hash_password("password123") != "password123"


def test_verify_password():
    hashed = hash_password("password123")
    assert verify_password("password123", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_same_password_hashes_differently():
    assert hash_password("password123") != hash_password("password123")


def test_token_round_trip():
    assert decode_access_token(create_access_token("42")) == "42"


def test_decode_rejects_garbage():
    assert decode_access_token("not-a-jwt") is None


def test_purpose_token_round_trip():
    token = create_purpose_token("7", "github_oauth", 10)
    assert decode_purpose_token(token, "github_oauth") == "7"


def test_purpose_token_rejects_other_purpose():
    assert decode_purpose_token(create_purpose_token("7", "github_oauth", 10), "other") is None


def test_purpose_token_is_not_a_login_token():
    assert decode_access_token(create_purpose_token("7", "github_oauth", 10)) is None


def test_login_token_is_not_a_purpose_token():
    assert decode_purpose_token(create_access_token("7"), "github_oauth") is None


def test_secret_encryption_round_trip():
    encrypted = encrypt_secret("gho_abc")
    assert encrypted != "gho_abc"
    assert decrypt_secret(encrypted) == "gho_abc"


def test_decrypt_garbage_returns_none():
    assert decrypt_secret("garbage") is None
