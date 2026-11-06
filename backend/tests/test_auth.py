from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.models import User


def _login(client, email, password):
    return client.post("/api/auth/login", data={"username": email, "password": password})


def _make_token(sub, *, expires_in=timedelta(minutes=5), key=None):
    settings = get_settings()
    payload = {"sub": sub, "exp": datetime.now(timezone.utc) + expires_in}
    return jwt.encode(payload, key or settings.secret_key, algorithm=settings.jwt_algorithm)


def test_register_success(client, user_payload):
    res = client.post("/api/auth/register", json=user_payload)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == user_payload["email"]
    assert "password" not in body and "hashed_password" not in body


def test_register_duplicate_email(client, user_payload):
    client.post("/api/auth/register", json=user_payload)
    res = client.post("/api/auth/register", json=user_payload)
    assert res.status_code == 409


def test_register_duplicate_email_is_case_insensitive(client, user_payload):
    client.post("/api/auth/register", json=user_payload)
    res = client.post("/api/auth/register", json={**user_payload, "email": "TEST@Example.com"})
    assert res.status_code == 409


@pytest.mark.parametrize("field, value", [("email", "not-an-email"), ("password", "short"), ("full_name", "")])
def test_register_rejects_invalid_input(client, user_payload, field, value):
    res = client.post("/api/auth/register", json={**user_payload, field: value})
    assert res.status_code == 422


def test_password_is_stored_hashed(client, db, user_payload):
    client.post("/api/auth/register", json=user_payload)
    user = db.scalar(select(User).where(User.email == user_payload["email"]))
    assert user.hashed_password != user_payload["password"]
    assert user.hashed_password.startswith("$argon2")


def test_login_success(client, user_payload):
    client.post("/api/auth/register", json=user_payload)
    res = _login(client, user_payload["email"], user_payload["password"])
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"
    assert res.json()["access_token"]


def test_login_wrong_password(client, user_payload):
    client.post("/api/auth/register", json=user_payload)
    assert _login(client, user_payload["email"], "wrong-password").status_code == 401


def test_login_unknown_email_looks_identical_to_wrong_password(client, user_payload):
    client.post("/api/auth/register", json=user_payload)
    wrong_pw = _login(client, user_payload["email"], "wrong-password")
    unknown = _login(client, "nobody@example.com", "password123")
    assert unknown.status_code == wrong_pw.status_code == 401
    assert unknown.json() == wrong_pw.json()


def test_login_email_is_case_insensitive(client, user_payload):
    client.post("/api/auth/register", json=user_payload)
    assert _login(client, "TEST@EXAMPLE.COM", user_payload["password"]).status_code == 200


def test_login_inactive_user(client, db, user_payload):
    client.post("/api/auth/register", json=user_payload)
    user = db.scalar(select(User).where(User.email == user_payload["email"]))
    user.is_active = False
    db.commit()
    assert _login(client, user_payload["email"], user_payload["password"]).status_code == 401


def test_me_with_valid_token(client, auth_headers, user_payload):
    res = client.get("/api/users/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == user_payload["email"]


def test_me_without_token(client):
    assert client.get("/api/users/me").status_code == 401


def test_me_with_garbage_token(client):
    assert client.get("/api/users/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_me_with_expired_token(client, user_payload):
    user_id = client.post("/api/auth/register", json=user_payload).json()["id"]
    token = _make_token(str(user_id), expires_in=timedelta(minutes=-1))
    assert client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_me_with_token_signed_by_wrong_key(client, user_payload):
    user_id = client.post("/api/auth/register", json=user_payload).json()["id"]
    token = _make_token(str(user_id), key="a-different-secret-key-0123456789abcdef")
    assert client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_me_with_token_for_nonexistent_user(client):
    res = client.get("/api/users/me", headers={"Authorization": f"Bearer {_make_token('9999')}"})
    assert res.status_code == 401


def test_me_rejects_deactivated_user(client, db, auth_headers, user_payload):
    user = db.scalar(select(User).where(User.email == user_payload["email"]))
    user.is_active = False
    db.commit()
    assert client.get("/api/users/me", headers=auth_headers).status_code == 401
