"""README generation: ask the LLM for a Markdown README based on the repo's files."""
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_readme_service
from app.models.user import User
from app.schemas.readme import ReadmeRead
from app.services.readme_service import ReadmeService

router = APIRouter(prefix="/readme", tags=["readme"])


@router.get("/{repo_id}", response_model=ReadmeRead)
def get_readme(repo_id: int, user: User = Depends(get_current_user), service: ReadmeService = Depends(get_readme_service)):
    doc = service.get_readme(user, repo_id)
    if doc is None:
        raise HTTPException(404, "No README has been generated for this repository yet")
    return doc


@router.post("/{repo_id}/generate", response_model=ReadmeRead)
def generate_readme(repo_id: int, user: User = Depends(get_current_user), service: ReadmeService = Depends(get_readme_service)):
    """Synchronous: a README is one LLM call, fast enough to return directly."""
    return service.generate(user, repo_id)
