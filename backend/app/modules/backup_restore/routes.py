"""API routes for the Backup & Restore module."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.backup_restore.repository import BackupRestoreRepository
from app.modules.backup_restore.schemas import BackupRestoreHealthRead
from app.modules.backup_restore.service import BackupRestoreService

router = APIRouter()


def get_backup_restore_service(
    db: Session = Depends(get_db),
) -> BackupRestoreService:
    repository = BackupRestoreRepository(db)
    return BackupRestoreService(repository)


@router.get("/health", response_model=BackupRestoreHealthRead)
def module_health(
    service: BackupRestoreService = Depends(get_backup_restore_service),
    _: User = Depends(get_current_user),
) -> BackupRestoreHealthRead:
    return service.health()
