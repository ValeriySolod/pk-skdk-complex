"""Pydantic schemas for the Backup & Restore module API contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.backup_restore.models import (
    BackupJobStatus,
    BackupJobType,
    RestoreJobStatus,
)


class BackupRestoreHealthRead(BaseModel):
    """Backup & Restore module health response."""

    status: str
    module: str


class BackupJobBase(BaseModel):
    """Shared backup job API fields."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    backup_type: BackupJobType = BackupJobType.MANUAL
    status: BackupJobStatus = BackupJobStatus.PENDING
    storage_location: str | None = Field(default=None, max_length=255)
    storage_path: str | None = Field(default=None, max_length=1024)
    artifact_name: str | None = Field(default=None, max_length=255)
    file_size_bytes: int | None = Field(default=None, ge=0)
    checksum: str | None = Field(default=None, max_length=128)
    config: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    error_message: str | None = None
    created_by_id: int | None = Field(default=None, ge=1)
    updated_by_id: int | None = Field(default=None, ge=1)
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BackupJobCreate(BackupJobBase):
    """Payload for creating a backup job record."""


class BackupJobUpdate(BaseModel):
    """Payload for partially updating a backup job."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    backup_type: BackupJobType | None = None
    status: BackupJobStatus | None = None
    storage_location: str | None = Field(default=None, max_length=255)
    storage_path: str | None = Field(default=None, max_length=1024)
    artifact_name: str | None = Field(default=None, max_length=255)
    file_size_bytes: int | None = Field(default=None, ge=0)
    checksum: str | None = Field(default=None, max_length=128)
    config: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    error_message: str | None = None
    updated_by_id: int | None = Field(default=None, ge=1)
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BackupJobStatusUpdate(BaseModel):
    """Payload for updating backup job lifecycle status."""

    status: BackupJobStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result_summary: dict[str, Any] | None = None
    error_message: str | None = None
    storage_location: str | None = Field(default=None, max_length=255)
    storage_path: str | None = Field(default=None, max_length=1024)
    artifact_name: str | None = Field(default=None, max_length=255)
    file_size_bytes: int | None = Field(default=None, ge=0)
    checksum: str | None = Field(default=None, max_length=128)
    updated_by_id: int | None = Field(default=None, ge=1)


class BackupJobRead(BackupJobBase):
    """Response schema for a backup job."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_uuid: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class BackupJobListResponse(BaseModel):
    """Paginated backup job response."""

    items: list[BackupJobRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class BackupJobFilterParams(BaseModel):
    """Query parameters for listing backup jobs."""

    title: str | None = Field(default=None, max_length=255)
    backup_type: BackupJobType | None = None
    status: BackupJobStatus | None = None
    storage_location: str | None = Field(default=None, max_length=255)
    artifact_name: str | None = Field(default=None, max_length=255)
    checksum: str | None = Field(default=None, max_length=128)
    created_by_id: int | None = Field(default=None, ge=1)
    updated_by_id: int | None = Field(default=None, ge=1)
    scheduled_from: datetime | None = None
    scheduled_to: datetime | None = None
    started_from: datetime | None = None
    started_to: datetime | None = None
    completed_from: datetime | None = None
    completed_to: datetime | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    include_deleted: bool = False
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class RestoreJobBase(BaseModel):
    """Shared restore job API fields."""

    backup_job_id: int | None = Field(default=None, ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    status: RestoreJobStatus = RestoreJobStatus.PENDING
    restore_scope: str = Field(..., min_length=1, max_length=120)
    target_environment: str | None = Field(default=None, max_length=120)
    source_artifact_name: str | None = Field(default=None, max_length=255)
    source_storage_path: str | None = Field(default=None, max_length=1024)
    config: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    error_message: str | None = None
    created_by_id: int | None = Field(default=None, ge=1)
    updated_by_id: int | None = Field(default=None, ge=1)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class RestoreJobCreate(RestoreJobBase):
    """Payload for creating a restore job record."""


class RestoreJobUpdate(BaseModel):
    """Payload for partially updating a restore job."""

    backup_job_id: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: RestoreJobStatus | None = None
    restore_scope: str | None = Field(default=None, min_length=1, max_length=120)
    target_environment: str | None = Field(default=None, max_length=120)
    source_artifact_name: str | None = Field(default=None, max_length=255)
    source_storage_path: str | None = Field(default=None, max_length=1024)
    config: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    error_message: str | None = None
    updated_by_id: int | None = Field(default=None, ge=1)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class RestoreJobStatusUpdate(BaseModel):
    """Payload for updating restore job lifecycle status."""

    status: RestoreJobStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result_summary: dict[str, Any] | None = None
    error_message: str | None = None
    updated_by_id: int | None = Field(default=None, ge=1)


class RestoreJobRead(RestoreJobBase):
    """Response schema for a restore job."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_uuid: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class RestoreJobListResponse(BaseModel):
    """Paginated restore job response."""

    items: list[RestoreJobRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class RestoreJobFilterParams(BaseModel):
    """Query parameters for listing restore jobs."""

    backup_job_id: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, max_length=255)
    status: RestoreJobStatus | None = None
    restore_scope: str | None = Field(default=None, max_length=120)
    target_environment: str | None = Field(default=None, max_length=120)
    source_artifact_name: str | None = Field(default=None, max_length=255)
    created_by_id: int | None = Field(default=None, ge=1)
    updated_by_id: int | None = Field(default=None, ge=1)
    started_from: datetime | None = None
    started_to: datetime | None = None
    completed_from: datetime | None = None
    completed_to: datetime | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    include_deleted: bool = False
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


BackupJobResponse = BackupJobRead
RestoreJobResponse = RestoreJobRead


__all__ = [
    "BackupJobCreate",
    "BackupJobFilterParams",
    "BackupJobListResponse",
    "BackupJobRead",
    "BackupJobResponse",
    "BackupJobStatusUpdate",
    "BackupJobUpdate",
    "BackupRestoreHealthRead",
    "RestoreJobCreate",
    "RestoreJobFilterParams",
    "RestoreJobListResponse",
    "RestoreJobRead",
    "RestoreJobResponse",
    "RestoreJobStatusUpdate",
    "RestoreJobUpdate",
]
