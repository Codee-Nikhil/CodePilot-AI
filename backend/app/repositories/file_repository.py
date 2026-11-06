from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.models.repo import RepoFile
from app.utils.repo_files import ParsedFile, SyncCounts


class FileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_tree(self, repo_id: int):
        stmt = (
            select(RepoFile.path, RepoFile.size, RepoFile.language)
            .where(RepoFile.repo_id == repo_id)
            .order_by(RepoFile.path)
        )
        return list(self.db.execute(stmt).all())

    def get_by_path(self, repo_id: int, path: str) -> RepoFile | None:
        return self.db.scalar(select(RepoFile).where(RepoFile.repo_id == repo_id, RepoFile.path == path))

    def get_many_by_paths(self, repo_id: int, paths: list[str]) -> list[RepoFile]:
        stmt = select(RepoFile).where(RepoFile.repo_id == repo_id, RepoFile.path.in_(paths))
        return list(self.db.scalars(stmt))

    def count_for_repo(self, repo_id: int) -> int:
        return len(self.list_tree(repo_id))

    def count_for_user(self, user_id: int) -> int:
        from app.models.repo import Repo
        stmt = (
            select(RepoFile.id).join(Repo, Repo.id == RepoFile.repo_id).where(Repo.user_id == user_id)
        )
        return len(list(self.db.scalars(stmt)))

    def list_needing_index(self, repo_id: int, limit: int) -> list[RepoFile]:
        stmt = (
            select(RepoFile)
            .where(RepoFile.repo_id == repo_id, RepoFile.indexed_hash.is_distinct_from(RepoFile.content_hash))
            .order_by(RepoFile.id)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def reset_index(self, repo_id: int) -> None:
        self.db.execute(update(RepoFile).where(RepoFile.repo_id == repo_id).values(indexed_hash=None))
        self.db.commit()

    def sync(self, repo_id: int, files: dict[str, ParsedFile]) -> SyncCounts:
        existing = dict(
            self.db.execute(
                select(RepoFile.path, RepoFile.content_hash).where(RepoFile.repo_id == repo_id)
            ).all()
        )
        removed = [path for path in existing if path not in files]
        if removed:
            self.db.execute(delete(RepoFile).where(RepoFile.repo_id == repo_id, RepoFile.path.in_(removed)))

        added = updated = 0
        for path, parsed in files.items():
            values = dict(
                size=parsed.size, language=parsed.language,
                content=parsed.content, content_hash=parsed.content_hash,
            )
            if path not in existing:
                self.db.add(RepoFile(repo_id=repo_id, path=path, **values))
                added += 1
            elif existing[path] != parsed.content_hash:
                self.db.execute(
                    update(RepoFile).where(RepoFile.repo_id == repo_id, RepoFile.path == path).values(**values)
                )
                updated += 1
        self.db.commit()
        return SyncCounts(added=added, updated=updated, removed=len(removed))
