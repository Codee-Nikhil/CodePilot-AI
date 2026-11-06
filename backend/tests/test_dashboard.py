def test_requires_auth(client):
    assert client.get("/api/dashboard/stats").status_code == 401


def test_stats_start_at_zero(client, auth_headers):
    res = client.get("/api/dashboard/stats", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == {"repositories": 0, "files_analyzed": 0, "reviews": 0, "chats": 0}


def test_stats_reflect_activity(client, connected_headers, fake_ai):
    repo_id = client.post("/api/repositories", json={"full_name": "octocat/demo"}, headers=connected_headers).json()["id"]
    client.post("/api/reviews", json={"repo_id": repo_id, "paths": ["src/main.py"]}, headers=connected_headers)
    client.post(
        "/api/chat/stream", json={"repo_id": repo_id, "chat_id": None, "message": "hi"}, headers=connected_headers
    )
    stats = client.get("/api/dashboard/stats", headers=connected_headers).json()
    assert stats == {"repositories": 1, "files_analyzed": 3, "reviews": 1, "chats": 1}


def test_stats_are_scoped_per_user(client, connected_headers, other_auth_headers):
    client.post("/api/repositories", json={"full_name": "octocat/demo"}, headers=connected_headers)
    assert client.get("/api/dashboard/stats", headers=other_auth_headers).json()["repositories"] == 0
