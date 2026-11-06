"""Chunk, embed and store repository files. Incremental: only changed files are re-embedded."""
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import update

from app.ai import providers
from app.ai.chunker import chunk_text
from app.core.exceptions import DomainError
from app.database.session import SessionLocal
from app.models.repo import Repo, RepoFile
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.file_repository import FileRepository
from app.repositories.repo_repository import RepoRepository

logger = logging.getLogger(__name__)
FILES_PER_BATCH = 20


class IndexingService:
    def __init__(self, repos: RepoRepository, files: FileRepository, embeddings: EmbeddingRepository, embedder, store) -> None:
        self.repos = repos
        self.files = files
        self.embeddings = embeddings
        self.embedder = embedder
        self.store = store

    def index_repo(self, repo_id: int) -> None:
        repo = self.repos.get(repo_id)
        if repo is None:
            return

        if repo.embedding_model != self.embedder.name:
            self.embeddings.delete_for_repo(repo.id)
            self.files.reset_index(repo.id)
            repo = self.repos.update(repo, embedding_model=self.embedder.name)

        orphans = self.embeddings.orphan_chroma_ids(repo.id)
        if orphans:
            self.store.delete(orphans)
            self.embeddings.delete_orphans(repo.id)

        while (batch := self.files.list_needing_index(repo.id, FILES_PER_BATCH)):
            self._index_batch(repo, batch)

        self.repos.update(repo, index_status="ready", index_error=None, indexed_at=datetime.now(timezone.utc))

    def _index_batch(self, repo: Repo, files: list[RepoFile]) -> None:
        stale_ids = self.embeddings.chroma_ids_for_files([f.id for f in files])
        if stale_ids:
            self.store.delete(stale_ids)

        rows: list[dict] = []
        ids: list[str] = []
        texts: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []
        for file in files:
            for index, chunk in enumerate(chunk_text(file.content)):
                chroma_id = uuid.uuid4().hex
                ids.append(chroma_id)
                documents.append(chunk.text)
                texts.append(f"{file.path}\n{chunk.text}")
                metadatas.append({
                    "repo_id": repo.id, "file_id": file.id, "path": file.path,
                    "start_line": chunk.start_line, "end_line": chunk.end_line,
                })
                rows.append({
                    "file_id": file.id, "chunk_index": index, "chroma_id": chroma_id,
                    "start_line": chunk.start_line, "end_line": chunk.end_line,
                })

        if texts:
            vectors = self.embedder.embed_documents(texts)
            self.store.add(ids=ids, embeddings=vectors, documents=documents, metadatas=metadatas)
        self.embeddings.replace_for_files(repo.id, files, rows)


def run_index_job(repo_id: int) -> None:
    with SessionLocal() as db:
        repos = RepoRepository(db)
        try:
            IndexingService(
                repos, FileRepository(db), EmbeddingRepository(db),
                providers.get_embedder(), providers.get_vector_store(),
            ).index_repo(repo_id)
        except Exception as exc:
            logger.exception("Indexing repo %s failed", repo_id)
            db.rollback()
            repo = repos.get(repo_id)
            if repo is not None:
                message = str(exc) if isinstance(exc, DomainError) else "Indexing failed unexpectedly. Check the server logs"
                repos.update(repo, index_status="failed", index_error=message[:500])


def recover_interrupted_jobs() -> None:
    with SessionLocal() as db:
        db.execute(
            update(Repo).where(Repo.index_status == "indexing")
            .values(index_status="failed", index_error="Interrupted by a server restart. Re-index to retry")
        )
        db.commit()
