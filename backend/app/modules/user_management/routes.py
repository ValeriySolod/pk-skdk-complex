from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.user_management.repository import UserManagementRepository
from app.modules.user_management.schemas import UserManagementHealthRead, UserRead
from app.modules.user_management.service import UserManagementService


router = APIRouter()


def get_user_management_service(
    db: Session = Depends(get_db),
) -> UserManagementService:
    repository = UserManagementRepository(db)
    return UserManagementService(repository)


@router.get("/health", response_model=UserManagementHealthRead)
def module_health(
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    return service.health()


@router.get("/users", response_model=list[UserRead])
def list_users(
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    return service.list_users()


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    user = service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
