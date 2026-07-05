from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.file_storage.repository import FileStorageRepository
from app.modules.file_storage.schemas import FileStorageHealthRead
from app.modules.file_storage.service import FileStorageService


router = APIRouter()


def get_file_storage_service(
    db: Session = Depends(get_db),
) -> FileStorageService:
    repository = FileStorageRepository(db)
    return FileStorageService(repository)


@router.get("/health", response_model=FileStorageHealthRead)
def module_health(
    service: FileStorageService = Depends(get_file_storage_service),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    return service.health()
