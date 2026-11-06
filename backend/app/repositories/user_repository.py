from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError, GitHubAccountInUseError
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def create(self, *, email: str, full_name: str, hashed_password: str) -> User:
        user = User(email=email, full_name=full_name, hashed_password=hashed_password)
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise EmailAlreadyRegisteredError() from None
        self.db.refresh(user)
        return user

    def set_github(self, user: User, *, github_id: int, login: str, token_encrypted: str) -> None:
        user.github_id = github_id
        user.github_login = login
        user.github_token_encrypted = token_encrypted
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise GitHubAccountInUseError() from None

    def clear_github(self, user: User) -> None:
        user.github_id = None
        user.github_login = None
        user.github_token_encrypted = None
        self.db.commit()

    def update_profile(self, user: User, *, full_name: str) -> User:
        user.full_name = full_name
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, *, hashed_password: str) -> None:
        user.hashed_password = hashed_password
        self.db.commit()

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
