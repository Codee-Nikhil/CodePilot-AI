"""Reusable FastAPI dependencies."""
from fastapi import BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.ai import providers
from app.core.config import get_settings
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.file_repository import FileRepository
from app.repositories.readme_repository import ReadmeRepository
from app.repositories.repo_repository import RepoRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.dashboard_service import DashboardService
from app.services.github_client import GitHubClient
from app.services.github_service import GitHubService
from app.services.indexing_service import run_index_job
from app.services.readme_service import ReadmeService
from app.services.repo_service import RepoService
from app.services.review_service import ReviewService, run_review_job
from app.services.settings_service import SettingsService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_repo_repository(db: Session = Depends(get_db)) -> RepoRepository:
    return RepoRepository(db)


def get_file_repository(db: Session = Depends(get_db)) -> FileRepository:
    return FileRepository(db)


def get_review_repository(db: Session = Depends(get_db)) -> ReviewRepository:
    return ReviewRepository(db)


def get_readme_repository(db: Session = Depends(get_db)) -> ReadmeRepository:
    return ReadmeRepository(db)


def get_github_client() -> GitHubClient:
    return GitHubClient()


def get_auth_service(users: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(users)


def get_github_service(
    users: UserRepository = Depends(get_user_repository),
    github: GitHubClient = Depends(get_github_client),
) -> GitHubService:
    return GitHubService(users, github)


def get_repo_service(
    background: BackgroundTasks,
    repos: RepoRepository = Depends(get_repo_repository),
    files: FileRepository = Depends(get_file_repository),
    github: GitHubClient = Depends(get_github_client),
) -> RepoService:
    return RepoService(
        repos, files, github,
        store_factory=providers.get_vector_store,
        enqueue_index=lambda repo_id: background.add_task(run_index_job, repo_id),
    )


def get_chat_service(
    db: Session = Depends(get_db),
    repos: RepoRepository = Depends(get_repo_repository),
) -> ChatService:
    return ChatService(ChatRepository(db), repos, get_settings().rag_top_k)


def get_review_service(
    reviews: ReviewRepository = Depends(get_review_repository),
    repos: RepoRepository = Depends(get_repo_repository),
    files: FileRepository = Depends(get_file_repository),
) -> ReviewService:
    return ReviewService(reviews, repos, files)


def get_readme_service(
    readmes: ReadmeRepository = Depends(get_readme_repository),
    repos: RepoRepository = Depends(get_repo_repository),
    files: FileRepository = Depends(get_file_repository),
) -> ReadmeService:
    return ReadmeService(readmes, repos, files)


def get_dashboard_service(
    repos: RepoRepository = Depends(get_repo_repository),
    files: FileRepository = Depends(get_file_repository),
    reviews: ReviewRepository = Depends(get_review_repository),
    db: Session = Depends(get_db),
) -> DashboardService:
    return DashboardService(repos, files, reviews, ChatRepository(db))


def get_settings_service(users: UserRepository = Depends(get_user_repository)) -> SettingsService:
    return SettingsService(users)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise unauthorized
    user = users.get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise unauthorized
    return user
