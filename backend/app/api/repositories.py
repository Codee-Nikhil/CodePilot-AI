from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_repo_service
from app.models.user import User
from app.schemas.repo import FileContent, FileNode, RepoImport, RepoRead, SyncResult
from app.services.repo_service import RepoService

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.get("", response_model=list[RepoRead])
def list_repositories(user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service)):
    return service.list_repos(user)


@router.post("", response_model=RepoRead, status_code=201)
def import_repository(data: RepoImport, user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service)):
    return service.import_repo(user, data.full_name)


@router.get("/{repo_id}", response_model=RepoRead)
def get_repository(repo_id: int, user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service)):
    return service.get_repo(user, repo_id)


@router.post("/{repo_id}/sync", response_model=SyncResult)
def sync_repository(repo_id: int, user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service)):
    return service.sync_repo(user, repo_id)


@router.delete("/{repo_id}", status_code=204)
def delete_repository(repo_id: int, user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service)):
    service.delete_repo(user, repo_id)


@router.get("/{repo_id}/tree", response_model=list[FileNode])
def get_tree(repo_id: int, user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service)):
    return service.get_tree(user, repo_id)


@router.get("/{repo_id}/file", response_model=FileContent)
def get_file(
    repo_id: int, path: str = Query(min_length=1, max_length=1024),
    user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service),
):
    return service.get_file(user, repo_id, path)


@router.post("/{repo_id}/index", response_model=RepoRead, status_code=202)
def reindex_repository(repo_id: int, user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service)):
    return service.reindex_repo(user, repo_id)
