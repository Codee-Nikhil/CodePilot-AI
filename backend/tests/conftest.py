"""Shared fixtures. Tests run against a separate database, never the dev one."""
import os

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://codepilot:codepilot@localhost:5432/codepilot_test",
)
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production-0123456789"

from cryptography.fernet import Fernet  # noqa: E402

os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
os.environ["GITHUB_CLIENT_ID"] = "test-client-id"
os.environ["GITHUB_CLIENT_SECRET"] = "test-client-secret"
os.environ["GITHUB_OAUTH_SCOPE"] = "public_repo"

from types import SimpleNamespace  # noqa: E402
from urllib.parse import parse_qs, urlparse  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.ai import providers  # noqa: E402
from app.api.deps import get_github_client  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.database.session import SessionLocal, engine  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from app.models import *  # noqa: E402, F401, F403
from tests.fakes import FakeEmbedder, FakeGitHub, FakeLLM, FakeVectorStore  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    assert engine.url.database.endswith("_test"), "Refusing to run tests on a non-test database"
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    yield
    tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def fake_ai(monkeypatch):
    ai = SimpleNamespace(embedder=FakeEmbedder(), store=FakeVectorStore(), llm=FakeLLM())
    monkeypatch.setattr(providers, "get_embedder", lambda: ai.embedder)
    monkeypatch.setattr(providers, "get_vector_store", lambda: ai.store)
    monkeypatch.setattr(providers, "get_llm", lambda: ai.llm)
    return ai


@pytest.fixture
def client() -> TestClient:
    return TestClient(fastapi_app)


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture
def user_payload() -> dict:
    return {"email": "test@example.com", "full_name": "Test User", "password": "password123"}


@pytest.fixture
def auth_headers(client: TestClient, user_payload: dict) -> dict:
    client.post("/api/auth/register", json=user_payload)
    res = client.post(
        "/api/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def other_auth_headers(client: TestClient) -> dict:
    payload = {"email": "other@example.com", "full_name": "Other User", "password": "password123"}
    client.post("/api/auth/register", json=payload)
    res = client.post("/api/auth/login", data={"username": payload["email"], "password": payload["password"]})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def fake_github():
    fake = FakeGitHub()
    fastapi_app.dependency_overrides[get_github_client] = lambda: fake
    yield fake
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def connected_headers(client: TestClient, auth_headers: dict, fake_github: FakeGitHub) -> dict:
    url = client.get("/api/github/connect", headers=auth_headers).json()["url"]
    state = parse_qs(urlparse(url).query)["state"][0]
    res = client.get("/api/github/callback", params={"code": "good", "state": state}, follow_redirects=False)
    assert res.status_code == 302 and res.headers["location"].endswith("github=connected")
    return auth_headers
