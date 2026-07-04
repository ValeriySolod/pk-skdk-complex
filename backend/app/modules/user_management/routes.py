from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.user_management.repository import UserManagementRepository
from app.modules.user_management.schemas import (
    UserManagementAuditEventCreate,
    UserManagementAuditEventRead,
    UserManagementHealthRead,
    UserManagementProfileCreate,
    UserManagementProfileRead,
    UserManagementProfileUpdate,
    UserManagementRoleAssignmentCreate,
    UserManagementRoleAssignmentRead,
    UserManagementRoleAssignmentUpdate,
    UserRead,
)
from app.modules.user_management.service import UserManagementService


router = APIRouter()


def get_user_management_service(
    db: Session = Depends(get_db),
) -> UserManagementService:
    repository = UserManagementRepository(db)
    return UserManagementService(repository)


def raise_bad_request(exc: ValueError) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    ) from exc


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


@router.get("/profiles", response_model=list[UserManagementProfileRead])
def list_profiles(
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    return service.list_profiles()


@router.post(
    "/profiles",
    response_model=UserManagementProfileRead,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    payload: UserManagementProfileCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_user_management_service(db)
    try:
        profile = service.create_profile(payload)
    except ValueError as exc:
        raise_bad_request(exc)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profiles/{profile_id}", response_model=UserManagementProfileRead)
def get_profile(
    profile_id: int,
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    profile = service.get_profile(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User management profile not found",
        )
    return profile


@router.patch("/profiles/{profile_id}", response_model=UserManagementProfileRead)
def update_profile(
    profile_id: int,
    payload: UserManagementProfileUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_user_management_service(db)
    try:
        profile = service.update_profile(profile_id, payload)
    except ValueError as exc:
        raise_bad_request(exc)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User management profile not found",
        )
    db.commit()
    db.refresh(profile)
    return profile


@router.get(
    "/role-assignments",
    response_model=list[UserManagementRoleAssignmentRead],
)
def list_role_assignments(
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    return service.list_role_assignments()


@router.post(
    "/role-assignments",
    response_model=UserManagementRoleAssignmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_role_assignment(
    payload: UserManagementRoleAssignmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_user_management_service(db)
    try:
        role_assignment = service.create_role_assignment(payload)
    except ValueError as exc:
        raise_bad_request(exc)
    db.commit()
    db.refresh(role_assignment)
    return role_assignment


@router.get(
    "/role-assignments/{assignment_id}",
    response_model=UserManagementRoleAssignmentRead,
)
def get_role_assignment(
    assignment_id: int,
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    role_assignment = service.get_role_assignment(assignment_id)
    if role_assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User management role assignment not found",
        )
    return role_assignment


@router.patch(
    "/role-assignments/{assignment_id}",
    response_model=UserManagementRoleAssignmentRead,
)
def update_role_assignment(
    assignment_id: int,
    payload: UserManagementRoleAssignmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_user_management_service(db)
    try:
        role_assignment = service.update_role_assignment(assignment_id, payload)
    except ValueError as exc:
        raise_bad_request(exc)
    if role_assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User management role assignment not found",
        )
    db.commit()
    db.refresh(role_assignment)
    return role_assignment


@router.get("/audit-events", response_model=list[UserManagementAuditEventRead])
def list_audit_events(
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    return service.list_audit_events()


@router.post(
    "/audit-events",
    response_model=UserManagementAuditEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_audit_event(
    payload: UserManagementAuditEventCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = get_user_management_service(db)
    try:
        audit_event = service.create_audit_event(payload)
    except ValueError as exc:
        raise_bad_request(exc)
    db.commit()
    db.refresh(audit_event)
    return audit_event


@router.get("/audit-events/{event_id}", response_model=UserManagementAuditEventRead)
def get_audit_event(
    event_id: int,
    service: UserManagementService = Depends(get_user_management_service),
    _: User = Depends(get_current_user),
):
    audit_event = service.get_audit_event(event_id)
    if audit_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User management audit event not found",
        )
    return audit_event
