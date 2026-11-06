def _import(client, headers):
    return client.post("/api/repositories", json={"full_name": "octocat/demo"}, headers=headers).json()["id"]


def test_requires_auth(client):
    assert client.post("/api/readme/1/generate").status_code == 401


def test_get_before_generate_returns_404(client, connected_headers):
    repo_id = _import(client, connected_headers)
    assert client.get(f"/api/readme/{repo_id}", headers=connected_headers).status_code == 404


def test_generate_and_fetch_readme(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    res = client.post(f"/api/readme/{repo_id}/generate", headers=connected_headers)
    assert res.status_code == 200
    assert res.json()["content"] == fake_ai.llm.complete_reply

    fetched = client.get(f"/api/readme/{repo_id}", headers=connected_headers)
    assert fetched.status_code == 200
    assert fetched.json()["content"] == fake_ai.llm.complete_reply


def test_regenerate_overwrites(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    client.post(f"/api/readme/{repo_id}/generate", headers=connected_headers)
    fake_ai.llm.complete_reply = "# New README\n"
    res = client.post(f"/api/readme/{repo_id}/generate", headers=connected_headers)
    assert res.json()["content"] == "# New README"  # generate() strips trailing whitespace
    assert client.get(f"/api/readme/{repo_id}", headers=connected_headers).json()["content"] == "# New README"


def test_other_users_cannot_access(client, connected_headers, other_auth_headers):
    repo_id = _import(client, connected_headers)
    client.post(f"/api/readme/{repo_id}/generate", headers=connected_headers)
    assert client.get(f"/api/readme/{repo_id}", headers=other_auth_headers).status_code == 404
    assert client.post(f"/api/readme/{repo_id}/generate", headers=other_auth_headers).status_code == 404
