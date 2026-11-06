from app.ai.embeddings import Embedder
from app.ai.vector_store import Hit, VectorStore


class Retriever:
    def __init__(self, embedder: Embedder, store: VectorStore, top_k: int) -> None:
        self.embedder = embedder
        self.store = store
        self.top_k = top_k

    def search(self, repo_id: int, query: str) -> list[Hit]:
        return self.store.query(repo_id, self.embedder.embed_query(query), self.top_k)
