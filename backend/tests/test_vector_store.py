import uuid

import chromadb

from app.ai.vector_store import VectorStore


def _meta(repo_id, path):
    return {"repo_id": repo_id, "file_id": 1, "path": path, "start_line": 1, "end_line": 2}


def test_query_is_scoped_to_one_repo_and_ranked():
    client = chromadb.EphemeralClient(settings=chromadb.Settings(anonymized_telemetry=False))
    store = VectorStore(client, f"test_{uuid.uuid4().hex}")
    store.add(
        ids=["a", "b", "c"], embeddings=[[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]], documents=["A", "B", "C"],
        metadatas=[_meta(1, "a.py"), _meta(1, "b.py"), _meta(2, "c.py")],
    )
    assert [h.path for h in store.query(1, [1.0, 0.0], 5)] == ["a.py", "b.py"]
    store.delete(["a"])
    assert [h.path for h in store.query(1, [1.0, 0.0], 5)] == ["b.py"]
    store.delete_repo(1)
    assert store.query(1, [1.0, 0.0], 5) == []
