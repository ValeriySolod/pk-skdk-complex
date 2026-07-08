"""API routes for the Backup & Restore module."""

from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.models import User
from app.modules.backup_restore.models import BackupJob, RestoreJob
from app.modules.backup_restore.repository import BackupRestoreRepository
from app.modules.backup_restore.schemas import (
    BackupJobCreate,
    BackupJobFilterParams,
    BackupJobListResponse,
    BackupJobResponse,
    BackupJobStatusUpdate,
    BackupJobUpdate,
    BackupRestoreHealthRead,
    RestoreJobCreate,
    RestoreJobFilterParams,
    RestoreJobListResponse,
    RestoreJobResponse,
    RestoreJobStatusUpdate,
    RestoreJobUpdate,
)
from app.modules.backup_restore.service import BackupRestoreService

router = APIRouter()


def get_backup_restore_service(
    db: Session = Depends(get_db),
) -> BackupRestoreService:
    repository = BackupRestoreRepository(db)
    return BackupRestoreService(repository)


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def backup_restore_write_conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


@router.get("/health", response_model=BackupRestoreHealthRead)
def module_health(
    service: BackupRestoreService = Depends(get_backup_restore_service),
    _: User = Depends(get_current_user),
) -> BackupRestoreHealthRead:
    return service.health()


@router.get("/backup-jobs", response_model=BackupJobListResponse)
def list_backup_jobs(
    filters: BackupJobFilterParams = Depends(),
    service: BackupRestoreService = Depends(get_backup_restore_service),
    _: User = Depends(get_current_user),
) -> BackupJobListResponse:
    filter_values = filters.model_dump()
    items = service.list_backup_jobs(**filter_values)
    total = service.count_backup_jobs(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return BackupJobListResponse(
        items=items,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/backup-jobs",
    response_model=BackupJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_backup_job(
    payload: BackupJobCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> BackupJob:
    service = get_backup_restore_service(db)
    try:
        job = service.create_backup_job(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise backup_restore_write_conflict("Backup job could not be persisted") from exc
    db.refresh(job)
    return job


@router.get(
    "/backup-jobs/uuid/{job_uuid}",
    response_model=BackupJobResponse,
)
def get_backup_job_by_uuid(
    job_uuid: UUID,
    service: BackupRestoreService = Depends(get_backup_restore_service),
    _: User = Depends(get_current_user),
) -> BackupJob:
    job = service.get_backup_job_by_uuid(job_uuid)
    if job is None:
        raise_not_found("Backup job not found")
    return job


@router.get("/backup-jobs/{job_id}", response_model=BackupJobResponse)
def get_backup_job(
    job_id: int,
    service: BackupRestoreService = Depends(get_backup_restore_service),
    _: User = Depends(get_current_user),
) -> BackupJob:
    job = service.get_backup_job(job_id)
    if job is None:
        raise_not_found("Backup job not found")
    return job


@router.patch("/backup-jobs/{job_id}", response_model=BackupJobResponse)
def update_backup_job(
    job_id: int,
    payload: BackupJobUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> BackupJob:
    service = get_backup_restore_service(db)
    try:
        job = service.update_backup_job(job_id, payload.model_dump(exclude_unset=True))
        if job is None:
            raise_not_found("Backup job not found")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise backup_restore_write_conflict("Backup job could not be persisted") from exc
    db.refresh(job)
    return job


@router.patch(
    "/backup-jobs/{job_id}/status",
    response_model=BackupJobResponse,
)
def update_backup_job_status(
    job_id: int,
    payload: BackupJobStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> BackupJob:
    service = get_backup_restore_service(db)
    job = service.mark_backup_job_status(
        job_id,
        payload.status.value,
        **payload.model_dump(exclude={"status"}, exclude_unset=True),
    )
    if job is None:
        raise_not_found("Backup job not found")
    db.commit()
    db.refresh(job)
    return job


@router.get("/restore-jobs", response_model=RestoreJobListResponse)
def list_restore_jobs(
    filters: RestoreJobFilterParams = Depends(),
    service: BackupRestoreService = Depends(get_backup_restore_service),
    _: User = Depends(get_current_user),
) -> RestoreJobListResponse:
    filter_values = filters.model_dump()
    items = service.list_restore_jobs(**filter_values)
    total = service.count_restore_jobs(
        **{
            key: value
            for key, value in filter_values.items()
            if key not in {"limit", "offset"}
        },
    )
    return RestoreJobListResponse(
        items=items,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.post(
    "/restore-jobs",
    response_model=RestoreJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_restore_job(
    payload: RestoreJobCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RestoreJob:
    service = get_backup_restore_service(db)
    if (
        payload.backup_job_id is not None
        and service.get_backup_job(payload.backup_job_id) is None
    ):
        raise_not_found("Backup job not found")
    try:
        job = service.create_restore_job(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise backup_restore_write_conflict("Restore job could not be persisted") from exc
    db.refresh(job)
    return job


@router.get(
    "/restore-jobs/uuid/{job_uuid}",
    response_model=RestoreJobResponse,
)
def get_restore_job_by_uuid(
    job_uuid: UUID,
    service: BackupRestoreService = Depends(get_backup_restore_service),
    _: User = Depends(get_current_user),
) -> RestoreJob:
    job = service.get_restore_job_by_uuid(job_uuid)
    if job is None:
        raise_not_found("Restore job not found")
    return job


@router.get("/restore-jobs/{job_id}", response_model=RestoreJobResponse)
def get_restore_job(
    job_id: int,
    service: BackupRestoreService = Depends(get_backup_restore_service),
    _: User = Depends(get_current_user),
) -> RestoreJob:
    job = service.get_restore_job(job_id)
    if job is None:
        raise_not_found("Restore job not found")
    return job


@router.patch("/restore-jobs/{job_id}", response_model=RestoreJobResponse)
def update_restore_job(
    job_id: int,
    payload: RestoreJobUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RestoreJob:
    service = get_backup_restore_service(db)
    if (
        payload.backup_job_id is not None
        and service.get_backup_job(payload.backup_job_id) is None
    ):
        raise_not_found("Backup job not found")
    try:
        job = service.update_restore_job(job_id, payload.model_dump(exclude_unset=True))
        if job is None:
            raise_not_found("Restore job not found")
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise backup_restore_write_conflict("Restore job could not be persisted") from exc
    db.refresh(job)
    return job


@router.patch(
    "/restore-jobs/{job_id}/status",
    response_model=RestoreJobResponse,
)
def update_restore_job_status(
    job_id: int,
    payload: RestoreJobStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RestoreJob:
    service = get_backup_restore_service(db)
    job = service.mark_restore_job_status(
        job_id,
        payload.status.value,
        **payload.model_dump(exclude={"status"}, exclude_unset=True),
    )
    if job is None:
        raise_not_found("Restore job not found")
    db.commit()
    db.refresh(job)
    return job
