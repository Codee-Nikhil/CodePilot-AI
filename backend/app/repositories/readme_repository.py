from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.readme import ReadmeDoc


class ReadmeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_repo(self, repo_id: int) -> ReadmeDoc | None:
        return self.db.scalar(select(ReadmeDoc).where(ReadmeDoc.repo_id == repo_id))

    def upsert(self, repo_id: int, content: str) -> ReadmeDoc:
        doc = self.get_for_repo(repo_id)
        if doc is None:
            doc = ReadmeDoc(repo_id=repo_id, content=content)
            self.db.add(doc)
        else:
            doc.content = content
        self.db.commit()
        self.db.refresh(doc)
        return doc
