"""API routes for the Administration module."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.administration.repository import AdministrationRepository
from app.modules.administration.schemas import AdministrationHealthRead
from app.modules.administration.service import AdministrationService


router = APIRouter()


def get_administration_service(
    db: Session = Depends(get_db),
) -> AdministrationService:
    repository = AdministrationRepository(db)
    return AdministrationService(repository)


@router.get("/health", response_model=AdministrationHealthRead)
def module_health(
    service: AdministrationService = Depends(get_administration_service),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    return service.health()
