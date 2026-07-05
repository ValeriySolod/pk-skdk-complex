from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.notifications.repository import NotificationsRepository
from app.modules.notifications.schemas import NotificationsHealthRead
from app.modules.notifications.service import NotificationsService


router = APIRouter()


def get_notifications_service(
    db: Session = Depends(get_db),
) -> NotificationsService:
    repository = NotificationsRepository(db)
    return NotificationsService(repository)


@router.get("/health", response_model=NotificationsHealthRead)
def module_health(
    service: NotificationsService = Depends(get_notifications_service),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    return service.health()
