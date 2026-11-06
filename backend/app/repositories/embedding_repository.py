from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.embedding import Embedding
from app.models.repo import RepoFile


class EmbeddingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def chroma_ids_for_files(self, file_ids: list[int]) -> list[str]:
        if not file_ids:
            return []
        return list(self.db.scalars(select(Embedding.chroma_id).where(Embedding.file_id.in_(file_ids))))

    def orphan_chroma_ids(self, repo_id: int) -> list[str]:
        stmt = select(Embedding.chroma_id).where(Embedding.repo_id == repo_id, Embedding.file_id.is_(None))
        return list(self.db.scalars(stmt))

    def delete_orphans(self, repo_id: int) -> None:
        self.db.execute(delete(Embedding).where(Embedding.repo_id == repo_id, Embedding.file_id.is_(None)))
        self.db.commit()

    def replace_for_files(self, repo_id: int, files: list[RepoFile], rows: list[dict]) -> None:
        self.db.execute(delete(Embedding).where(Embedding.file_id.in_([f.id for f in files])))
        self.db.add_all(Embedding(repo_id=repo_id, **row) for row in rows)
        for file in files:
            file.indexed_hash = file.content_hash
        self.db.commit()

    def delete_for_repo(self, repo_id: int) -> None:
        self.db.execute(delete(Embedding).where(Embedding.repo_id == repo_id))
        self.db.commit()
