"""Password hashing, JWTs, and secret encryption."""
from datetime import datetime, timedelta, timezone

import jwt
from cryptography.fernet import Fernet, InvalidToken
from pwdlib import PasswordHash

from app.core.config import get_settings

settings = get_settings()
_password_hash = PasswordHash.recommended()
_fernet = Fernet(settings.encryption_key.encode())


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_hash.verify(plain, hashed)


def _encode(subject: str, expires_in: timedelta, **claims: str) -> str:
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + expires_in, **claims}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def _decode(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None


def create_access_token(subject: str) -> str:
    return _encode(subject, timedelta(minutes=settings.access_token_expire_minutes))


def decode_access_token(token: str) -> str | None:
    payload = _decode(token)
    if payload is None or "purpose" in payload:
        return None
    return payload.get("sub")


def create_purpose_token(subject: str, purpose: str, expires_minutes: int) -> str:
    return _encode(subject, timedelta(minutes=expires_minutes), purpose=purpose)


def decode_purpose_token(token: str, purpose: str) -> str | None:
    payload = _decode(token)
    if payload is None or payload.get("purpose") != purpose:
        return None
    return payload.get("sub")


def encrypt_secret(value: str) -> str:
    return _fernet.encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str | None:
    try:
        return _fernet.decrypt(value.encode()).decode()
    except InvalidToken:
        return None
