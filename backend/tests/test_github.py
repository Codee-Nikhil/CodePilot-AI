from urllib.parse import parse_qs, urlparse

from sqlalchemy import select

from app.core.security import decrypt_secret
from app.models import User
from app.services.github_client import GitHubClient


def _state(client, headers):
    url = client.get("/api/github/connect", headers=headers).json()["url"]
    return parse_qs(urlparse(url).query)["state"][0]


def _callback(client, **params):
    return client.get("/api/github/callback", params=params, follow_redirects=False)


def test_connect_requires_auth(client):
    assert client.get("/api/github/connect").status_code == 401


def test_real_client_builds_authorize_url():
    query = parse_qs(urlparse(GitHubClient().authorize_url("abc")).query)
    assert query["client_id"] == ["test-client-id"]
    assert query["scope"] == ["public_repo"]
    assert query["state"] == ["abc"]


def test_callback_links_account_and_encrypts_token(client, auth_headers, fake_github, db, user_payload):
    res = _callback(client, code="good", state=_state(client, auth_headers))
    assert res.status_code == 302
    assert res.headers["location"].endswith("/repositories?github=connected")
    assert client.get("/api/users/me", headers=auth_headers).json()["github_login"] == "octocat"
    user = db.scalar(select(User).where(User.email == user_payload["email"]))
    assert user.github_token_encrypted != "gho_faketoken"
    assert decrypt_secret(user.github_token_encrypted) == "gho_faketoken"


def test_callback_rejects_garbage_state(client, auth_headers, fake_github):
    res = _callback(client, code="good", state="garbage")
    assert res.headers["location"].endswith("github=error")
    assert client.get("/api/users/me", headers=auth_headers).json()["github_login"] is None


def test_callback_rejects_login_token_as_state(client, auth_headers, fake_github):
    login_token = auth_headers["Authorization"].split()[1]
    assert _callback(client, code="good", state=login_token).headers["location"].endswith("github=error")


def test_callback_denied_by_user(client, fake_github):
    assert _callback(client, error="access_denied", state="x").headers["location"].endswith("github=denied")


def test_callback_bad_code(client, auth_headers, fake_github):
    res = _callback(client, code="bad", state=_state(client, auth_headers))
    assert res.headers["location"].endswith("github=error")


def test_same_github_account_cannot_link_twice(client, connected_headers, other_auth_headers, fake_github):
    res = _callback(client, code="good", state=_state(client, other_auth_headers))
    assert res.headers["location"].endswith("github=in_use")


def test_oauth_state_cannot_be_used_to_log_in(client, auth_headers, fake_github):
    state = _state(client, auth_headers)
    assert client.get("/api/users/me", headers={"Authorization": f"Bearer {state}"}).status_code == 401


def test_disconnect(client, connected_headers):
    assert client.delete("/api/github/connection", headers=connected_headers).status_code == 204
    assert client.get("/api/users/me", headers=connected_headers).json()["github_login"] is None
    assert client.get("/api/github/repos", headers=connected_headers).status_code == 409


def test_remote_repos_require_connection(client, auth_headers, fake_github):
    assert client.get("/api/github/repos", headers=auth_headers).status_code == 409
