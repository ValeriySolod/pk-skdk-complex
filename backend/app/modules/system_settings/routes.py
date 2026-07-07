"""API routes for the System Settings module."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.system_settings.repository import SystemSettingsRepository
from app.modules.system_settings.schemas import SystemSettingsHealthRead
from app.modules.system_settings.service import SystemSettingsService

router = APIRouter()


def get_system_settings_service(
    db: Session = Depends(get_db),
) -> SystemSettingsService:
    repository = SystemSettingsRepository(db)
    return SystemSettingsService(repository)


@router.get("/health", response_model=SystemSettingsHealthRead)
def module_health(
    service: SystemSettingsService = Depends(get_system_settings_service),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    return service.health()
