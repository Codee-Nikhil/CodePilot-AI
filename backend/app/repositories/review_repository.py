from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.review import Review, ReviewFinding


class ReviewRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_repo(self, user_id: int, repo_id: int) -> list[Review]:
        stmt = (
            select(Review).where(Review.user_id == user_id, Review.repo_id == repo_id)
            .order_by(Review.id.desc())
        )
        return list(self.db.scalars(stmt))

    def count_for_user(self, user_id: int) -> int:
        return len(list(self.db.scalars(select(Review.id).where(Review.user_id == user_id))))

    def get(self, review_id: int) -> Review | None:
        """Unscoped lookup, for background jobs only. Request handlers use get_for_user."""
        return self.db.get(Review, review_id)

    def get_for_user(self, user_id: int, review_id: int) -> Review | None:
        stmt = (
            select(Review).where(Review.id == review_id, Review.user_id == user_id)
            .options(selectinload(Review.findings))
        )
        return self.db.scalar(stmt)

    def create(self, user_id: int, repo_id: int, paths: list[str]) -> Review:
        review = Review(user_id=user_id, repo_id=repo_id, paths=paths, status="pending")
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def mark_running(self, review: Review) -> None:
        review.status = "running"
        self.db.commit()

    def complete(self, review: Review, *, summary: str, score: int | None, findings: list[dict]) -> Review:
        from datetime import datetime, timezone

        review.status = "completed"
        review.summary = summary
        review.score = score
        review.completed_at = datetime.now(timezone.utc)
        review.findings = [ReviewFinding(**f) for f in findings]
        self.db.commit()
        self.db.refresh(review)
        return review

    def fail(self, review: Review, error: str) -> None:
        from datetime import datetime, timezone

        review.status = "failed"
        review.error = error[:1000]
        review.completed_at = datetime.now(timezone.utc)
        self.db.commit()

    def delete(self, review: Review) -> None:
        self.db.delete(review)
        self.db.commit()
