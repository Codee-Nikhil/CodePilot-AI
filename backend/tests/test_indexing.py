from sqlalchemy import func, select

from app.models import Embedding, Repo

ALL_PATHS = {"README.md", "src/main.py", "src/utils/helpers.py"}


def _import(client, headers):
    return client.post("/api/repositories", json={"full_name": "octocat/demo"}, headers=headers).json()


def _get(client, headers, repo_id):
    return client.get(f"/api/repositories/{repo_id}", headers=headers).json()


def _sync(client, headers, repo_id):
    return client.post(f"/api/repositories/{repo_id}/sync", headers=headers)


def _embedded_paths(fake_ai):
    return {text.split("\n")[0] for text in fake_ai.embedder.embedded}


def test_import_indexes_in_the_background(client, connected_headers, fake_ai, db):
    repo = _import(client, connected_headers)
    assert repo["index_status"] == "indexing"
    ready = _get(client, connected_headers, repo["id"])
    assert ready["index_status"] == "ready" and ready["indexed_at"]
    assert _embedded_paths(fake_ai) == ALL_PATHS
    rows = db.scalar(select(func.count()).select_from(Embedding))
    assert rows > 0 and rows == fake_ai.store.count(repo["id"])


def test_sync_reembeds_only_changed_files(client, connected_headers, fake_github, fake_ai):
    repo_id = _import(client, connected_headers)["id"]
    fake_ai.embedder.embedded.clear()
    fake_github.files["README.md"] = b"# Changed\n"
    _sync(client, connected_headers, repo_id)
    assert _embedded_paths(fake_ai) == {"README.md"}


def test_sync_without_changes_does_not_reindex(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)["id"]
    fake_ai.embedder.embedded.clear()
    _sync(client, connected_headers, repo_id)
    assert fake_ai.embedder.embedded == []


def test_vectors_of_deleted_files_are_removed(client, connected_headers, fake_github, fake_ai):
    repo_id = _import(client, connected_headers)["id"]
    del fake_github.files["src/main.py"]
    _sync(client, connected_headers, repo_id)
    paths = {item["path"] for item in fake_ai.store.items.values()}
    assert "src/main.py" not in paths and "README.md" in paths


def test_failed_indexing_is_recorded_and_can_be_retried(client, connected_headers, fake_ai):
    fake_ai.embedder.fail = True
    repo_id = _import(client, connected_headers)["id"]
    failed = _get(client, connected_headers, repo_id)
    assert failed["index_status"] == "failed" and "boom" in failed["index_error"]

    fake_ai.embedder.fail = False
    res = client.post(f"/api/repositories/{repo_id}/index", headers=connected_headers)
    assert res.status_code == 202
    assert _get(client, connected_headers, repo_id)["index_status"] == "ready"


def test_reindex_while_indexing_conflicts(client, connected_headers, db):
    repo_id = _import(client, connected_headers)["id"]
    repo = db.get(Repo, repo_id)
    repo.index_status = "indexing"
    db.commit()
    assert client.post(f"/api/repositories/{repo_id}/index", headers=connected_headers).status_code == 409


def test_changing_the_embedding_model_reindexes_everything(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)["id"]
    fake_ai.embedder.embedded.clear()
    fake_ai.embedder.name = "fake-v2"
    client.post(f"/api/repositories/{repo_id}/index", headers=connected_headers)
    assert _embedded_paths(fake_ai) == ALL_PATHS


def test_deleting_a_repo_removes_its_vectors(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)["id"]
    assert fake_ai.store.count(repo_id) > 0
    client.delete(f"/api/repositories/{repo_id}", headers=connected_headers)
    assert fake_ai.store.count(repo_id) == 0
