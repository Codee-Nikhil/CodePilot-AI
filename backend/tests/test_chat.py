import json

from app.ai import providers
from app.core.exceptions import LLMNotConfiguredError

QUESTION = "how does the add function work"


def _import(client, headers):
    return client.post("/api/repositories", json={"full_name": "octocat/demo"}, headers=headers).json()["id"]


def _post(client, headers, repo_id, message, chat_id=None):
    return client.post("/api/chat/stream", json={"repo_id": repo_id, "chat_id": chat_id, "message": message}, headers=headers)


def _ask(client, headers, repo_id, message, chat_id=None):
    res = _post(client, headers, repo_id, message, chat_id)
    assert res.status_code == 200, res.text
    return [json.loads(line) for line in res.text.splitlines() if line]


def test_requires_auth(client):
    assert client.post("/api/chat/stream", json={"repo_id": 1, "message": "hi"}).status_code == 401


def test_streams_answer_with_ranked_sources(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    events = _ask(client, connected_headers, repo_id, QUESTION)
    assert events[0]["type"] == "meta" and events[-1]["type"] == "done"
    assert events[0]["sources"][0]["path"] == "src/utils/helpers.py"
    answer = "".join(e["text"] for e in events if e["type"] == "token")
    assert answer.strip() == fake_ai.llm.reply


def test_prompt_contains_retrieved_code_and_never_skipped_files(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    _ask(client, connected_headers, repo_id, QUESTION)
    system, messages = fake_ai.llm.calls[0]
    prompt = messages[-1].content
    assert "def add(a, b)" in prompt and f"Question: {QUESTION}" in prompt
    assert "module.exports" not in prompt
    assert "untrusted" in system


def test_answer_is_saved_and_follow_ups_include_history(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    chat_id = _ask(client, connected_headers, repo_id, QUESTION)[0]["chat_id"]
    detail = client.get(f"/api/chat/{chat_id}", headers=connected_headers).json()
    assert [m["role"] for m in detail["messages"]] == ["user", "assistant"]
    assert detail["messages"][1]["sources"]

    _ask(client, connected_headers, repo_id, "and what about main?", chat_id=chat_id)
    _, messages = fake_ai.llm.calls[1]
    assert [m.role for m in messages] == ["user", "assistant", "user"]


def test_chat_requires_an_indexed_repo(client, connected_headers, fake_ai):
    fake_ai.embedder.fail = True
    repo_id = _import(client, connected_headers)
    assert _post(client, connected_headers, repo_id, QUESTION).status_code == 409


def test_llm_error_is_streamed_and_no_answer_saved(client, connected_headers, fake_ai):
    repo_id = _import(client, connected_headers)
    fake_ai.llm.fail = True
    events = _ask(client, connected_headers, repo_id, QUESTION)
    assert events[-1]["type"] == "error"
    detail = client.get(f"/api/chat/{events[0]['chat_id']}", headers=connected_headers).json()
    assert [m["role"] for m in detail["messages"]] == ["user"]


def test_missing_ai_key_returns_503(client, connected_headers, monkeypatch):
    repo_id = _import(client, connected_headers)

    def no_key():
        raise LLMNotConfiguredError()

    monkeypatch.setattr(providers, "get_llm", no_key)
    assert _post(client, connected_headers, repo_id, QUESTION).status_code == 503


def test_blank_message_is_rejected(client, connected_headers):
    repo_id = _import(client, connected_headers)
    assert _post(client, connected_headers, repo_id, "   ").status_code == 422


def test_list_and_delete_chats(client, connected_headers):
    repo_id = _import(client, connected_headers)
    chat_id = _ask(client, connected_headers, repo_id, QUESTION)[0]["chat_id"]
    listed = client.get(f"/api/chat?repo_id={repo_id}", headers=connected_headers).json()
    assert [c["id"] for c in listed] == [chat_id]
    assert client.delete(f"/api/chat/{chat_id}", headers=connected_headers).status_code == 204
    assert client.get(f"/api/chat/{chat_id}", headers=connected_headers).status_code == 404


def test_other_users_are_locked_out(client, connected_headers, other_auth_headers):
    repo_id = _import(client, connected_headers)
    chat_id = _ask(client, connected_headers, repo_id, QUESTION)[0]["chat_id"]
    assert _post(client, other_auth_headers, repo_id, "hi").status_code == 404
    assert client.get(f"/api/chat/{chat_id}", headers=other_auth_headers).status_code == 404
    assert client.delete(f"/api/chat/{chat_id}", headers=other_auth_headers).status_code == 404
    assert client.get(f"/api/chat?repo_id={repo_id}", headers=other_auth_headers).json() == []
