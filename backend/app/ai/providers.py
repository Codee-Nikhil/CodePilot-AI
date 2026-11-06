"""Factories for the AI building blocks. Cached, and replaced by fakes in tests.
Always call them as `providers.get_x()` so tests can patch them."""
from functools import lru_cache

import chromadb

from app.ai.embeddings import Embedder, GeminiEmbedder, LocalEmbedder, embedding_id
from app.ai.llm import LLM, GeminiLLM
from app.ai.vector_store import VectorStore
from app.core.config import get_settings
from app.core.exceptions import LLMNotConfiguredError


@lru_cache
def get_embedder() -> Embedder:
    settings = get_settings()
    if settings.embedding_provider == "gemini":
        if not settings.gemini_api_key:
            raise LLMNotConfiguredError()
        return GeminiEmbedder(settings.gemini_api_key, settings.gemini_embedding_model)
    return LocalEmbedder(settings.local_embedding_model)


@lru_cache
def get_vector_store() -> VectorStore:
    settings = get_settings()
    gemini = settings.embedding_provider == "gemini"
    model = settings.gemini_embedding_model if gemini else settings.local_embedding_model
    client = chromadb.PersistentClient(
        path=settings.chroma_path, settings=chromadb.Settings(anonymized_telemetry=False)
    )
    return VectorStore(client, f"chunks_{embedding_id(settings.embedding_provider, model)}")


@lru_cache
def get_llm() -> LLM:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise LLMNotConfiguredError()
    return GeminiLLM(settings.gemini_api_key, settings.llm_model)
