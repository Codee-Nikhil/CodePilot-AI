"""Turn text into vectors. Providers are interchangeable behind the Embedder protocol."""
import math
from collections.abc import Sequence
from typing import Protocol

from app.core.exceptions import EmbeddingError


class Embedder(Protocol):
    name: str

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


def embedding_id(provider: str, model: str) -> str:
    return f"{provider}-{model.split('/')[-1]}"


def _normalize(vector: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


class LocalEmbedder:
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self.name = embedding_id("local", model_name)
        self._model = SentenceTransformer(model_name)
        self._model.max_seq_length = 512

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class GeminiEmbedder:
    BATCH = 100

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai

        self.name = embedding_id("gemini", model)
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        from google.genai import errors

        vectors: list[list[float]] = []
        for i in range(0, len(texts), self.BATCH):
            try:
                res = self._client.models.embed_content(model=self._model, contents=texts[i : i + self.BATCH])
            except errors.APIError as exc:
                raise EmbeddingError("Embedding request failed (check the API key and quota)") from exc
            vectors.extend(_normalize(e.values) for e in res.embeddings)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
