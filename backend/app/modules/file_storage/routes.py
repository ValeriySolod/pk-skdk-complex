from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.file_storage.models import FileObject
from app.modules.file_storage.repository import FileStorageRepository
from app.modules.file_storage.schemas import (
    FileObjectCreate,
    FileObjectFilterParams,
    FileObjectListResponse,
    FileObjectResponse,
    FileStorageHealthRead,
)
from app.modules.file_storage.service import FileStorageService


router = APIRouter()


def get_file_storage_service(
    db: Session = Depends(get_db),
) -> FileStorageService:
    repository = FileStorageRepository(db)
    return FileStorageService(repository)


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


@router.get("/health", response_model=FileStorageHealthRead)
def module_health(
    service: FileStorageService = Depends(get_file_storage_service),
    _: User = Depends(get_current_user),
) -> dict[str, str]:
    return service.health()


@router.get("/objects", response_model=FileObjectListResponse)
def list_file_objects(
    filters: FileObjectFilterParams = Depends(),
    service: FileStorageService = Depends(get_file_storage_service),
    _: User = Depends(get_current_user),
) -> FileObjectListResponse:
    filter_values = filters.model_dump()
    file_objects = service.list_file_objects(**filter_values)
    total = service.count_file_objects(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return FileObjectListResponse(
        items=file_objects,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/objects",
    response_model=FileObjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_file_object(
    payload: FileObjectCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> FileObject:
    service = get_file_storage_service(db)
    file_object = service.create_file_object(FileObject(**payload.model_dump()))
    db.commit()
    db.refresh(file_object)
    return file_object


@router.get("/objects/uuid/{object_uuid}", response_model=FileObjectResponse)
def get_file_object_by_uuid(
    object_uuid: UUID,
    service: FileStorageService = Depends(get_file_storage_service),
    _: User = Depends(get_current_user),
) -> FileObject:
    file_object = service.get_file_object_by_uuid(object_uuid)
    if file_object is None:
        raise_not_found("File object not found")
    return file_object


@router.get("/objects/{object_id}", response_model=FileObjectResponse)
def get_file_object(
    object_id: int,
    service: FileStorageService = Depends(get_file_storage_service),
    _: User = Depends(get_current_user),
) -> FileObject:
    file_object = service.get_file_object(object_id)
    if file_object is None:
        raise_not_found("File object not found")
    return file_object
