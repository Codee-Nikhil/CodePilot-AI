from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import RepoAlreadyImportedError
from app.models.repo import Repo


class RepoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(self, user_id: int) -> list[Repo]:
        return list(self.db.scalars(select(Repo).where(Repo.user_id == user_id).order_by(Repo.id.desc())))

    def get_for_user(self, user_id: int, repo_id: int) -> Repo | None:
        return self.db.scalar(select(Repo).where(Repo.id == repo_id, Repo.user_id == user_id))

    def get(self, repo_id: int) -> Repo | None:
        return self.db.get(Repo, repo_id)

    def imported_github_ids(self, user_id: int) -> set[int]:
        return set(self.db.scalars(select(Repo.github_id).where(Repo.user_id == user_id)))

    def count_for_user(self, user_id: int) -> int:
        return len(self.list_for_user(user_id))

    def create(self, **fields) -> Repo:
        repo = Repo(**fields)
        self.db.add(repo)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise RepoAlreadyImportedError() from None
        self.db.refresh(repo)
        return repo

    def update(self, repo: Repo, **fields) -> Repo:
        for key, value in fields.items():
            setattr(repo, key, value)
        self.db.commit()
        self.db.refresh(repo)
        return repo

    def delete(self, repo: Repo) -> None:
        self.db.delete(repo)
        self.db.commit()
