"""Profile updates, password changes, and account deletion."""
from app.core.exceptions import WrongPasswordError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class SettingsService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def update_profile(self, user: User, full_name: str) -> User:
        return self.users.update_profile(user, full_name=full_name.strip())

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise WrongPasswordError()
        self.users.update_password(user, hashed_password=hash_password(new_password))

    def delete_account(self, user: User, password: str) -> None:
        if not verify_password(password, user.hashed_password):
            raise WrongPasswordError()
        self.users.delete(user)
