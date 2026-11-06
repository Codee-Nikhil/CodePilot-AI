import pytest
from sqlalchemy import func, select

from app.models import RepoFile


def _import(client, headers, full_name="octocat/demo"):
    return client.post("/api/repositories", json={"full_name": full_name}, headers=headers)


def _tree(client, headers, repo_id):
    return client.get(f"/api/repositories/{repo_id}/tree", headers=headers).json()


def test_requires_auth(client):
    assert client.get("/api/repositories").status_code == 401


def test_import_requires_github_connection(client, auth_headers, fake_github):
    assert _import(client, auth_headers).status_code == 409


def test_import_stores_only_useful_text_files(client, connected_headers):
    res = _import(client, connected_headers)
    assert res.status_code == 201
    assert res.json()["full_name"] == "octocat/demo"
    tree = _tree(client, connected_headers, res.json()["id"])
    assert {f["path"] for f in tree} == {"README.md", "src/main.py", "src/utils/helpers.py"}
    assert next(f for f in tree if f["path"] == "src/main.py")["language"] == "python"


def test_import_rejects_malformed_name(client, connected_headers):
    assert _import(client, connected_headers, "../../etc/passwd").status_code == 422


def test_import_unknown_repo(client, connected_headers):
    assert _import(client, connected_headers, "octocat/nope").status_code == 404


def test_import_twice_conflicts(client, connected_headers):
    _import(client, connected_headers)
    assert _import(client, connected_headers).status_code == 409


def test_failed_import_leaves_nothing_behind(client, connected_headers, fake_github):
    fake_github.fail_download = True
    assert _import(client, connected_headers).status_code == 502
    assert client.get("/api/repositories", headers=connected_headers).json() == []


def test_remote_list_marks_imported(client, connected_headers):
    assert client.get("/api/github/repos", headers=connected_headers).json()[0]["imported"] is False
    _import(client, connected_headers)
    assert client.get("/api/github/repos", headers=connected_headers).json()[0]["imported"] is True


def test_get_file_content(client, connected_headers):
    repo_id = _import(client, connected_headers).json()["id"]
    res = client.get(f"/api/repositories/{repo_id}/file", params={"path": "src/main.py"}, headers=connected_headers)
    assert res.status_code == 200
    assert res.json()["content"] == "print('hi')\n"


def test_get_missing_file(client, connected_headers):
    repo_id = _import(client, connected_headers).json()["id"]
    res = client.get(f"/api/repositories/{repo_id}/file", params={"path": "nope.py"}, headers=connected_headers)
    assert res.status_code == 404


def test_sync_without_changes(client, connected_headers):
    repo_id = _import(client, connected_headers).json()["id"]
    res = client.post(f"/api/repositories/{repo_id}/sync", headers=connected_headers)
    assert res.json() == {"added": 0, "updated": 0, "removed": 0}


def test_sync_detects_added_updated_removed(client, connected_headers, fake_github):
    repo_id = _import(client, connected_headers).json()["id"]
    fake_github.files["README.md"] = b"# Changed\n"
    fake_github.files["new.py"] = b"x = 1\n"
    del fake_github.files["src/main.py"]
    res = client.post(f"/api/repositories/{repo_id}/sync", headers=connected_headers)
    assert res.json() == {"added": 1, "updated": 1, "removed": 1}
    readme = client.get(f"/api/repositories/{repo_id}/file", params={"path": "README.md"}, headers=connected_headers)
    assert readme.json()["content"] == "# Changed\n"


def test_delete_cascades_to_files(client, connected_headers, db):
    repo_id = _import(client, connected_headers).json()["id"]
    assert client.delete(f"/api/repositories/{repo_id}", headers=connected_headers).status_code == 204
    assert client.get(f"/api/repositories/{repo_id}", headers=connected_headers).status_code == 404
    assert db.scalar(select(func.count()).select_from(RepoFile)) == 0


def test_users_only_see_their_own_repos(client, connected_headers, other_auth_headers):
    _import(client, connected_headers)
    assert client.get("/api/repositories", headers=other_auth_headers).json() == []


@pytest.mark.parametrize("method, suffix", [
    ("get", ""), ("get", "/tree"), ("get", "/file?path=README.md"), ("post", "/sync"),
    ("post", "/index"), ("delete", ""),
])
def test_other_users_get_404(client, connected_headers, other_auth_headers, method, suffix):
    repo_id = _import(client, connected_headers).json()["id"]
    res = getattr(client, method)(f"/api/repositories/{repo_id}{suffix}", headers=other_auth_headers)
    assert res.status_code == 404
