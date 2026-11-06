"""AI code review: start a review (runs in the background) and read structured results."""
from fastapi import APIRouter, BackgroundTasks, Depends

from app.api.deps import get_current_user, get_review_service
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewDetail, ReviewSummary
from app.services.review_service import ReviewService, run_review_job

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewSummary])
def list_reviews(repo_id: int, user: User = Depends(get_current_user), service: ReviewService = Depends(get_review_service)):
    return service.list_reviews(user, repo_id)


@router.post("", response_model=ReviewSummary, status_code=202)
def start_review(
    data: ReviewCreate, background: BackgroundTasks,
    user: User = Depends(get_current_user), service: ReviewService = Depends(get_review_service),
):
    review = service.start_review(user, data.repo_id, data.paths)
    background.add_task(run_review_job, review.id)
    return review


@router.get("/{review_id}", response_model=ReviewDetail)
def get_review(review_id: int, user: User = Depends(get_current_user), service: ReviewService = Depends(get_review_service)):
    return service.get_review(user, review_id)


@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, user: User = Depends(get_current_user), service: ReviewService = Depends(get_review_service)):
    service.delete_review(user, review_id)
