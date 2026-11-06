"""Connecting and disconnecting a user's GitHub account."""
from app.core.config import get_settings
from app.core.exceptions import (
    GitHubAuthError, GitHubNotConfiguredError, GitHubNotConnectedError, InvalidStateError,
)
from app.core.security import (
    create_purpose_token, decode_purpose_token, decrypt_secret, encrypt_secret,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.github_client import GitHubClient

OAUTH_PURPOSE = "github_oauth"


def get_github_token(user: User) -> str:
    if not user.github_token_encrypted:
        raise GitHubNotConnectedError()
    token = decrypt_secret(user.github_token_encrypted)
    if token is None:
        raise GitHubAuthError()
    return token


class GitHubService:
    def __init__(self, users: UserRepository, github: GitHubClient) -> None:
        self.users = users
        self.github = github

    def connect_url(self, user: User) -> str:
        settings = get_settings()
        if not (settings.github_client_id and settings.github_client_secret):
            raise GitHubNotConfiguredError()
        state = create_purpose_token(str(user.id), OAUTH_PURPOSE, expires_minutes=10)
        return self.github.authorize_url(state)

    def complete_connection(self, code: str, state: str) -> None:
        user_id = decode_purpose_token(state, OAUTH_PURPOSE)
        user = self.users.get_by_id(int(user_id)) if user_id else None
        if user is None or not user.is_active:
            raise InvalidStateError()
        token = self.github.exchange_code(code)
        profile = self.github.get_user(token)
        self.users.set_github(
            user, github_id=profile["id"], login=profile["login"], token_encrypted=encrypt_secret(token)
        )

    def disconnect(self, user: User) -> None:
        token = decrypt_secret(user.github_token_encrypted) if user.github_token_encrypted else None
        if token:
            self.github.revoke_token(token)
        self.users.clear_github(user)
