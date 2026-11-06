"""ChromaDB wrapper. Vectors live here; Postgres keeps the bookkeeping."""
from dataclasses import dataclass

BATCH = 2000


@dataclass(frozen=True)
class Hit:
    path: str
    start_line: int
    end_line: int
    text: str


class VectorStore:
    def __init__(self, client, collection_name: str) -> None:
        self._collection = client.get_or_create_collection(name=collection_name)

    def add(self, *, ids, embeddings, documents, metadatas) -> None:
        for i in range(0, len(ids), BATCH):
            s = slice(i, i + BATCH)
            self._collection.add(ids=ids[s], embeddings=embeddings[s], documents=documents[s], metadatas=metadatas[s])

    def delete(self, ids: list[str]) -> None:
        for i in range(0, len(ids), BATCH):
            self._collection.delete(ids=ids[i : i + BATCH])

    def delete_repo(self, repo_id: int) -> None:
        self._collection.delete(where={"repo_id": repo_id})

    def query(self, repo_id: int, embedding: list[float], k: int) -> list[Hit]:
        res = self._collection.query(
            query_embeddings=[embedding], n_results=k, where={"repo_id": repo_id},
            include=["documents", "metadatas"],
        )
        return [
            Hit(path=m["path"], start_line=m["start_line"], end_line=m["end_line"], text=doc)
            for doc, m in zip(res["documents"][0], res["metadatas"][0])
        ]
