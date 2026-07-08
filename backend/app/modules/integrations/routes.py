"""API routes for the Integrations module."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.integrations.repository import IntegrationsRepository
from app.modules.integrations.schemas import IntegrationsHealthRead
from app.modules.integrations.service import IntegrationsService

router = APIRouter()


def get_integrations_service(
    db: Session = Depends(get_db),
) -> IntegrationsService:
    repository = IntegrationsRepository(db)
    return IntegrationsService(repository)


@router.get("/health", response_model=IntegrationsHealthRead)
def module_health(
    service: IntegrationsService = Depends(get_integrations_service),
    _: User = Depends(get_current_user),
) -> IntegrationsHealthRead:
    return service.health()
