from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.file_storage.models import (
    FileObjectStatus,
    FileObjectVisibility,
    StorageProvider,
)


class FileStorageHealthRead(BaseModel):
    status: str


class FileObjectBase(BaseModel):
    original_filename: str
    storage_key: str
    content_type: str | None = None
    extension: str | None = None
    size_bytes: int = Field(ge=0)
    checksum_sha256: str | None = None
    storage_provider: str = StorageProvider.LOCAL.value
    storage_bucket: str | None = None
    storage_path: str
    status: str = FileObjectStatus.PENDING.value
    access_scope: str = FileObjectVisibility.PRIVATE.value
    owner_user_id: int | None = None
    related_entity_type: str | None = None
    related_entity_id: str | None = None
    metadata_json: dict[str, Any] | None = None


class FileObjectCreate(FileObjectBase):
    pass


class FileObjectUpdate(BaseModel):
    original_filename: str | None = None
    content_type: str | None = None
    extension: str | None = None
    checksum_sha256: str | None = None
    storage_provider: str | None = None
    storage_bucket: str | None = None
    storage_path: str | None = None
    status: str | None = None
    access_scope: str | None = None
    owner_user_id: int | None = None
    related_entity_type: str | None = None
    related_entity_id: str | None = None
    metadata_json: dict[str, Any] | None = None


class FileObjectRead(FileObjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class FileObjectListResponse(BaseModel):
    items: list[FileObjectRead]
    total: int
    limit: int
    offset: int


class FileObjectFilterParams(BaseModel):
    owner_user_id: int | None = None
    access_scope: str | None = None
    storage_provider: str | None = None
    status: str | None = None
    content_type: str | None = None
    related_entity_type: str | None = None
    related_entity_id: str | None = None
    checksum_sha256: str | None = None
    storage_bucket: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    include_deleted: bool = False
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


FileObjectResponse = FileObjectRead
