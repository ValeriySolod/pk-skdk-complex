"""API routes for the Monitoring & Health module."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.monitoring_health.repository import MonitoringHealthRepository
from app.modules.monitoring_health.schemas import MonitoringHealthHealthRead
from app.modules.monitoring_health.service import MonitoringHealthService

router = APIRouter()


def get_monitoring_health_service(
    db: Session = Depends(get_db),
) -> MonitoringHealthService:
    repository = MonitoringHealthRepository(db)
    return MonitoringHealthService(repository)


@router.get("/health", response_model=MonitoringHealthHealthRead)
def module_health(
    service: MonitoringHealthService = Depends(get_monitoring_health_service),
    _: User = Depends(get_current_user),
) -> MonitoringHealthHealthRead:
    return service.health()
