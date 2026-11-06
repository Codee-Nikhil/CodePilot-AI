"""Business rules for registration and login."""
from app.core.exceptions import InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def register(self, data: UserCreate) -> User:
        return self.users.create(
            email=data.email.lower(),
            full_name=data.full_name.strip(),
            hashed_password=hash_password(data.password),
        )

    def authenticate(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email.lower())
        if user is None or not user.is_active or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        return create_access_token(str(user.id))
