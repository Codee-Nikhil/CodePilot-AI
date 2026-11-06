from fastapi import APIRouter, Depends, Response

from app.api.deps import get_current_user, get_settings_service
from app.models.user import User
from app.schemas.settings import AccountDelete, PasswordChange, ProfileUpdate
from app.schemas.user import UserRead
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.put("/profile", response_model=UserRead)
def update_profile(data: ProfileUpdate, user: User = Depends(get_current_user), service: SettingsService = Depends(get_settings_service)):
    return service.update_profile(user, data.full_name)


@router.put("/password", status_code=204)
def change_password(data: PasswordChange, user: User = Depends(get_current_user), service: SettingsService = Depends(get_settings_service)):
    service.change_password(user, data.current_password, data.new_password)


@router.post("/delete-account", status_code=204)
def delete_account(data: AccountDelete, user: User = Depends(get_current_user), service: SettingsService = Depends(get_settings_service)):
    service.delete_account(user, data.password)
