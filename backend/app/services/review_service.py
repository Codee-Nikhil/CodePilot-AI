"""AI code review: review selected files and store structured findings."""
import logging

from app.ai import providers
from app.ai.llm import LLMMessage
from app.ai.review_prompts import REVIEW_SYSTEM_PROMPT, ReviewParseError, build_review_prompt, parse_review_response
from app.core.exceptions import LLMError, ReviewNotFoundError
from app.database.session import SessionLocal
from app.models.review import Review
from app.models.user import User
from app.repositories.file_repository import FileRepository
from app.repositories.repo_repository import RepoRepository
from app.repositories.review_repository import ReviewRepository

logger = logging.getLogger(__name__)
MAX_CHARS_PER_FILE = 8000  # keeps the prompt bounded even for a large selected file


class ReviewService:
    def __init__(self, reviews: ReviewRepository, repos: RepoRepository, files: FileRepository) -> None:
        self.reviews = reviews
        self.repos = repos
        self.files = files

    def list_reviews(self, user: User, repo_id: int) -> list[Review]:
        return self.reviews.list_for_repo(user.id, repo_id)

    def get_review(self, user: User, review_id: int) -> Review:
        review = self.reviews.get_for_user(user.id, review_id)
        if review is None:
            raise ReviewNotFoundError()
        return review

    def delete_review(self, user: User, review_id: int) -> None:
        self.reviews.delete(self.get_review(user, review_id))

    def start_review(self, user: User, repo_id: int, paths: list[str]) -> Review:
        from app.core.exceptions import RepoNotFoundError, RepoFileNotFoundError

        repo = self.repos.get_for_user(user.id, repo_id)
        if repo is None:
            raise RepoNotFoundError()
        found = self.files.get_many_by_paths(repo.id, paths)
        if len(found) != len(set(paths)):
            raise RepoFileNotFoundError("One or more selected files were not found")
        return self.reviews.create(user.id, repo.id, paths)


def run_review_job(review_id: int) -> None:
    """Background-task entry point: run the AI review and persist structured results."""
    with SessionLocal() as db:
        reviews = ReviewRepository(db)
        review = reviews.get(review_id)
        if review is None:
            return
        reviews.mark_running(review)
        try:
            repo = RepoRepository(db).get(review.repo_id)
            files = FileRepository(db).get_many_by_paths(repo.id, review.paths)
            file_pairs = [(f.path, f.content[:MAX_CHARS_PER_FILE]) for f in files]
            prompt = build_review_prompt(repo.full_name, file_pairs)
            llm = providers.get_llm()
            raw = llm.complete(REVIEW_SYSTEM_PROMPT, [LLMMessage("user", prompt)])
            parsed = parse_review_response(raw, valid_paths={p for p, _ in file_pairs})
            reviews.complete(review, summary=parsed["summary"], score=parsed["score"], findings=parsed["findings"])
        except (LLMError, ReviewParseError) as exc:
            logger.warning("Review %s failed: %s", review_id, exc)
            reviews.fail(review, str(exc))
        except Exception:
            logger.exception("Review %s failed unexpectedly", review_id)
            reviews.fail(review, "The review could not be completed. Check the server logs")
