"""Aggregate counts for the dashboard."""
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.file_repository import FileRepository
from app.repositories.repo_repository import RepoRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.dashboard import DashboardStats


class DashboardService:
    def __init__(self, repos: RepoRepository, files: FileRepository, reviews: ReviewRepository, chats: ChatRepository) -> None:
        self.repos = repos
        self.files = files
        self.reviews = reviews
        self.chats = chats

    def get_stats(self, user: User) -> DashboardStats:
        return DashboardStats(
            repositories=self.repos.count_for_user(user.id),
            files_analyzed=self.files.count_for_user(user.id),
            reviews=self.reviews.count_for_user(user.id),
            chats=self.chats.count_for_user(user.id),
        )
