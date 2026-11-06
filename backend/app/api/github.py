from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.api.deps import get_current_user, get_github_service, get_repo_service
from app.core.config import get_settings
from app.core.exceptions import DomainError, GitHubAccountInUseError
from app.models.user import User
from app.schemas.repo import RemoteRepo
from app.services.github_service import GitHubService
from app.services.repo_service import RepoService

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/connect", response_model=dict[str, str])
def connect(user: User = Depends(get_current_user), service: GitHubService = Depends(get_github_service)):
    return {"url": service.connect_url(user)}


@router.get("/callback", include_in_schema=False)
def callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    service: GitHubService = Depends(get_github_service),
):
    target = f"{get_settings().frontend_origin}/repositories"
    if error or not code or not state:
        return RedirectResponse(f"{target}?github=denied", status_code=302)
    try:
        service.complete_connection(code, state)
    except GitHubAccountInUseError:
        outcome = "in_use"
    except DomainError:
        outcome = "error"
    else:
        outcome = "connected"
    return RedirectResponse(f"{target}?github={outcome}", status_code=302)


@router.delete("/connection", status_code=204)
def disconnect(user: User = Depends(get_current_user), service: GitHubService = Depends(get_github_service)):
    service.disconnect(user)


@router.get("/repos", response_model=list[RemoteRepo])
def list_remote_repos(user: User = Depends(get_current_user), service: RepoService = Depends(get_repo_service)):
    return service.list_remote(user)
