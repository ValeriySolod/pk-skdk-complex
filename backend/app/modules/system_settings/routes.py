"""API routes for the System Settings module."""

from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.system_settings.models import SystemSetting
from app.modules.system_settings.repository import SystemSettingsRepository
from app.modules.system_settings.schemas import (
    SystemSettingCountResponse,
    SystemSettingCreate,
    SystemSettingListResponse,
    SystemSettingRead,
    SystemSettingUpdate,
    SystemSettingsHealthRead,
)
from app.modules.system_settings.service import SystemSettingsService

router = APIRouter()


def get_system_settings_service(
    db: Session = Depends(get_db),
) -> SystemSettingsService:
    repository = SystemSettingsRepository(db)
    return SystemSettingsService(repository)


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def duplicate_setting_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="System setting with this category and key already exists",
    )


@router.get("/health", response_model=SystemSettingsHealthRead)
def module_health(
    service: SystemSettingsService = Depends(get_system_settings_service),
    _: User = Depends(get_current_user),
) -> dict[str, object]:
    return service.health()


@router.get("/settings", response_model=SystemSettingListResponse)
def list_settings(
    category: str | None = None,
    key: str | None = None,
    status: str | None = None,
    value_type: str | None = None,
    created_by_id: int | None = None,
    updated_by_id: int | None = None,
    include_deleted: bool = False,
    limit: int = 100,
    offset: int = 0,
    service: SystemSettingsService = Depends(get_system_settings_service),
    _: User = Depends(get_current_user),
) -> SystemSettingListResponse:
    filters = {
        "category": category,
        "key": key,
        "status": status,
        "value_type": value_type,
        "created_by_id": created_by_id,
        "updated_by_id": updated_by_id,
        "include_deleted": include_deleted,
    }
    items = service.list_settings(**filters, limit=limit, offset=offset)
    total = service.count_settings(**filters)
    return SystemSettingListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/settings",
    response_model=SystemSettingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_setting(
    payload: SystemSettingCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SystemSetting:
    service = get_system_settings_service(db)
    try:
        setting = service.create_setting(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise duplicate_setting_error() from exc
    db.refresh(setting)
    return setting


@router.get("/settings/count", response_model=SystemSettingCountResponse)
def count_settings(
    category: str | None = None,
    key: str | None = None,
    status: str | None = None,
    value_type: str | None = None,
    created_by_id: int | None = None,
    updated_by_id: int | None = None,
    include_deleted: bool = False,
    service: SystemSettingsService = Depends(get_system_settings_service),
    _: User = Depends(get_current_user),
) -> SystemSettingCountResponse:
    total = service.count_settings(
        category=category,
        key=key,
        status=status,
        value_type=value_type,
        created_by_id=created_by_id,
        updated_by_id=updated_by_id,
        include_deleted=include_deleted,
    )
    return SystemSettingCountResponse(total=total)


@router.get("/settings/uuid/{setting_uuid}", response_model=SystemSettingRead)
def get_setting_by_uuid(
    setting_uuid: UUID,
    service: SystemSettingsService = Depends(get_system_settings_service),
    _: User = Depends(get_current_user),
) -> SystemSetting:
    setting = service.get_setting_by_uuid(setting_uuid)
    if setting is None:
        raise_not_found("System setting not found")
    return setting


@router.get(
    "/settings/key/{category}/{setting_key}",
    response_model=SystemSettingRead,
)
def get_setting_by_key(
    category: str,
    setting_key: str,
    service: SystemSettingsService = Depends(get_system_settings_service),
    _: User = Depends(get_current_user),
) -> SystemSetting:
    setting = service.get_setting_by_key(category, setting_key)
    if setting is None:
        raise_not_found("System setting not found")
    return setting


@router.get("/settings/{setting_id}", response_model=SystemSettingRead)
def get_setting(
    setting_id: int,
    service: SystemSettingsService = Depends(get_system_settings_service),
    _: User = Depends(get_current_user),
) -> SystemSetting:
    setting = service.get_setting(setting_id)
    if setting is None:
        raise_not_found("System setting not found")
    return setting


@router.patch("/settings/{setting_id}", response_model=SystemSettingRead)
def update_setting(
    setting_id: int,
    payload: SystemSettingUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SystemSetting:
    service = get_system_settings_service(db)
    try:
        setting = service.update_setting(
            setting_id, payload.model_dump(exclude_unset=True)
        )
        if setting is None:
            raise_not_found("System setting not found")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise duplicate_setting_error() from exc
    db.refresh(setting)
    return setting


@router.delete("/settings/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(
    setting_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Response:
    service = get_system_settings_service(db)
    deleted = service.delete_setting(setting_id)
    if not deleted:
        raise_not_found("System setting not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
