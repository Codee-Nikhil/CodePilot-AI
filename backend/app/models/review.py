"""AI code review: a review covers one or more files and produces structured findings."""
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), index=True)
    paths: Mapped[list] = mapped_column(JSON)  # file paths included in this review
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    error: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    score: Mapped[int | None] = mapped_column()  # 0-100 overall quality score
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    findings: Mapped[list["ReviewFinding"]] = relationship(
        back_populates="review", cascade="all, delete-orphan", passive_deletes=True, order_by="ReviewFinding.id"
    )


class ReviewFinding(Base):
    __tablename__ = "review_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), index=True)
    path: Mapped[str] = mapped_column(String(1024))
    line: Mapped[int | None] = mapped_column()
    severity: Mapped[str] = mapped_column(String(20))  # critical | warning | suggestion
    category: Mapped[str] = mapped_column(String(50))  # bug | security | performance | style | maintainability
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    suggestion: Mapped[str | None] = mapped_column(Text)

    review: Mapped["Review"] = relationship(back_populates="findings")
