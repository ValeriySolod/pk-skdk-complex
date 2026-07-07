"""Pydantic schemas for the Administration module API contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AdministrationReferenceBase(BaseModel):
    """Shared administrated reference/catalog entry fields."""

    catalog: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: str = Field(default="active", min_length=1, max_length=50)
    metadata_json: dict[str, Any] | None = None


class AdministrationReferenceCreate(AdministrationReferenceBase):
    """Payload for creating an administrated reference/catalog entry."""


class AdministrationReferenceUpdate(BaseModel):
    """Payload for partially updating an administrated reference/catalog entry."""

    catalog: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None, min_length=1, max_length=50)
    metadata_json: dict[str, Any] | None = None


class AdministrationReferenceRead(AdministrationReferenceBase):
    """Response schema for an administrated reference/catalog entry."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class MaintenanceTaskBase(BaseModel):
    """Shared maintenance task fields."""

    code: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: str = Field(default="pending", min_length=1, max_length=50)
    priority: str | None = Field(default=None, max_length=50)
    scheduled_for: datetime | None = None
    completed_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None


class MaintenanceTaskCreate(MaintenanceTaskBase):
    """Payload for creating a maintenance task."""


class MaintenanceTaskUpdate(BaseModel):
    """Payload for partially updating a maintenance task."""

    code: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None, min_length=1, max_length=50)
    priority: str | None = Field(default=None, max_length=50)
    scheduled_for: datetime | None = None
    completed_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None


class MaintenanceTaskRead(MaintenanceTaskBase):
    """Response schema for a maintenance task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class AdminActionEventBase(BaseModel):
    """Shared append-only administration action event fields."""

    actor_user_id: int | None = None
    action: str = Field(..., min_length=1, max_length=100)
    target_type: str = Field(..., min_length=1, max_length=100)
    target_id: str | None = Field(default=None, max_length=100)
    description: str | None = None
    metadata_json: dict[str, Any] | None = None


class AdminActionEventCreate(AdminActionEventBase):
    """Payload for creating an administration action event."""


class AdminActionEventRead(AdminActionEventBase):
    """Response schema for an administration action event."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    created_at: datetime


class AdministrationHealthRead(BaseModel):
    """Administration module health response."""

    status: str
    references: bool | None = None
    maintenance_tasks: bool | None = None
    action_events: bool | None = None
