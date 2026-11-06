from app.ai.review_prompts import ReviewParseError


def _import(client, headers):
    return client.post("/api/repositories", json={"full_name": "octocat/demo"}, headers=headers).json()["id"]


def _start(client, headers, repo_id, paths):
    return client.post("/api/reviews", json={"repo_id": repo_id, "paths": paths}, headers=headers)


def test_requires_auth(client):
    assert client.post("/api/reviews", json={"repo_id": 1, "paths": ["a.py"]}).status_code == 401


def test_review_runs_and_stores_structured_findings(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    res = _start(client, connected_headers, repo_id, ["src/main.py"])
    assert res.status_code == 202
    review_id = res.json()["id"]

    detail = client.get(f"/api/reviews/{review_id}", headers=connected_headers).json()
    assert detail["status"] == "completed"
    assert detail["score"] == 80
    assert detail["findings"][0]["path"] == "src/main.py"
    assert detail["findings"][0]["severity"] == "warning"

    system, messages = fake_ai.llm.calls[0]
    assert "print('hi')" in messages[-1].content
    assert "untrusted" in system or "review" in system.lower()


def test_review_rejects_unknown_file(client, connected_headers):
    repo_id = _import(client, connected_headers)
    assert _start(client, connected_headers, repo_id, ["nope.py"]).status_code == 404


def test_review_requires_at_least_one_path(client, connected_headers):
    repo_id = _import(client, connected_headers)
    assert client.post("/api/reviews", json={"repo_id": repo_id, "paths": []}, headers=connected_headers).status_code == 422


def test_failed_llm_marks_review_failed(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    fake_ai.llm.fail = True
    review_id = _start(client, connected_headers, repo_id, ["src/main.py"]).json()["id"]
    detail = client.get(f"/api/reviews/{review_id}", headers=connected_headers).json()
    assert detail["status"] == "failed" and detail["error"]


def test_malformed_json_marks_review_failed(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    fake_ai.llm.complete_reply = "not json at all"
    review_id = _start(client, connected_headers, repo_id, ["src/main.py"]).json()["id"]
    detail = client.get(f"/api/reviews/{review_id}", headers=connected_headers).json()
    assert detail["status"] == "failed"


def test_list_and_delete_reviews(client, connected_headers):
    repo_id = _import(client, connected_headers)
    review_id = _start(client, connected_headers, repo_id, ["src/main.py"]).json()["id"]
    listed = client.get(f"/api/reviews?repo_id={repo_id}", headers=connected_headers).json()
    assert [r["id"] for r in listed] == [review_id]
    assert client.delete(f"/api/reviews/{review_id}", headers=connected_headers).status_code == 204
    assert client.get(f"/api/reviews/{review_id}", headers=connected_headers).status_code == 404


def test_other_users_cannot_see_or_start_reviews(client, connected_headers, other_auth_headers):
    repo_id = _import(client, connected_headers)
    review_id = _start(client, connected_headers, repo_id, ["src/main.py"]).json()["id"]
    assert client.get(f"/api/reviews/{review_id}", headers=other_auth_headers).status_code == 404
    assert _start(client, other_auth_headers, repo_id, ["src/main.py"]).status_code == 404
