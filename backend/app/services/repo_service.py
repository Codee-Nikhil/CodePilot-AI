"""Importing, syncing, indexing and reading repositories."""
import logging
import tarfile
from collections.abc import Callable
from datetime import datetime, timezone

from app.ai.vector_store import VectorStore
from app.core.exceptions import (
    GitHubAPIError, RepoAlreadyImportedError, RepoFileNotFoundError, RepoIndexingError, RepoNotFoundError,
)
from app.models.repo import Repo, RepoFile
from app.models.user import User
from app.repositories.file_repository import FileRepository
from app.repositories.repo_repository import RepoRepository
from app.schemas.repo import RemoteRepo
from app.services.github_client import GitHubClient
from app.services.github_service import get_github_token
from app.utils.repo_files import SyncCounts, extract_text_files

logger = logging.getLogger(__name__)


def _metadata(info: dict) -> dict:
    return {
        "full_name": info["full_name"],
        "name": info["name"],
        "description": info.get("description"),
        "language": info.get("language"),
        "default_branch": info["default_branch"],
        "html_url": info["html_url"],
        "is_private": info["private"],
        "stars": info["stargazers_count"],
    }


class RepoService:
    def __init__(
        self,
        repos: RepoRepository,
        files: FileRepository,
        github: GitHubClient,
        store_factory: Callable[[], VectorStore],
        enqueue_index: Callable[[int], None],
    ) -> None:
        self.repos = repos
        self.files = files
        self.github = github
        self.store_factory = store_factory
        self.enqueue_index = enqueue_index

    def list_repos(self, user: User) -> list[Repo]:
        return self.repos.list_for_user(user.id)

    def get_repo(self, user: User, repo_id: int) -> Repo:
        repo = self.repos.get_for_user(user.id, repo_id)
        if repo is None:
            raise RepoNotFoundError()
        return repo

    def get_tree(self, user: User, repo_id: int):
        return self.files.list_tree(self.get_repo(user, repo_id).id)

    def get_file(self, user: User, repo_id: int, path: str) -> RepoFile:
        repo = self.get_repo(user, repo_id)
        file = self.files.get_by_path(repo.id, path)
        if file is None:
            raise RepoFileNotFoundError()
        return file

    def delete_repo(self, user: User, repo_id: int) -> None:
        repo = self.get_repo(user, repo_id)
        try:
            self.store_factory().delete_repo(repo.id)
        except Exception:
            logger.warning("Could not delete vectors of repo %s", repo.id, exc_info=True)
        self.repos.delete(repo)

    def list_remote(self, user: User) -> list[RemoteRepo]:
        token = get_github_token(user)
        imported = self.repos.imported_github_ids(user.id)
        return [
            RemoteRepo(
                github_id=r["id"], full_name=r["full_name"], description=r.get("description"),
                language=r.get("language"), is_private=r["private"], stars=r["stargazers_count"],
                updated_at=r.get("updated_at"), imported=r["id"] in imported,
            )
            for r in self.github.list_repos(token)
        ]

    def import_repo(self, user: User, full_name: str) -> Repo:
        token = get_github_token(user)
        info = self.github.get_repo(token, full_name)
        if info["id"] in self.repos.imported_github_ids(user.id):
            raise RepoAlreadyImportedError()
        repo = self.repos.create(user_id=user.id, github_id=info["id"], **_metadata(info))
        try:
            self._sync_files(token, repo)
        except Exception:
            self.repos.delete(repo)
            raise
        return self._queue_index(repo)

    def sync_repo(self, user: User, repo_id: int) -> SyncCounts:
        repo = self.get_repo(user, repo_id)
        token = get_github_token(user)
        info = self.github.get_repo_by_id(token, repo.github_id)
        self.repos.update(repo, **_metadata(info))
        counts = self._sync_files(token, repo)
        if counts.added or counts.updated or counts.removed or repo.index_status in ("pending", "failed"):
            self._queue_index(repo)
        return counts

    def reindex_repo(self, user: User, repo_id: int) -> Repo:
        repo = self.get_repo(user, repo_id)
        if repo.index_status == "indexing":
            raise RepoIndexingError()
        return self._queue_index(repo)

    def _queue_index(self, repo: Repo) -> Repo:
        if repo.index_status == "indexing":
            return repo
        repo = self.repos.update(repo, index_status="indexing", index_error=None)
        self.enqueue_index(repo.id)
        return repo

    def _sync_files(self, token: str, repo: Repo) -> SyncCounts:
        archive = self.github.download_tarball(token, repo.full_name, repo.default_branch)
        try:
            parsed = extract_text_files(archive)
        except (tarfile.TarError, EOFError) as exc:
            raise GitHubAPIError("Could not read the repository archive") from exc
        counts = self.files.sync(repo.id, parsed)
        self.repos.update(repo, last_synced_at=datetime.now(timezone.utc))
        return counts
