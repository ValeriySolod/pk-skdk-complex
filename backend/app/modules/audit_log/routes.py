from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.audit_log.repository import AuditLogRepository
from app.modules.audit_log.schemas import AuditLogHealthRead
from app.modules.audit_log.service import AuditLogService


router = APIRouter()


def get_audit_log_service(
    db: Session = Depends(get_db),
) -> AuditLogService:
    repository = AuditLogRepository(db)
    return AuditLogService(repository)


@router.get("/health", response_model=AuditLogHealthRead)
def module_health(
    service: AuditLogService = Depends(get_audit_log_service),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    return service.health()
