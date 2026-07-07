"""Pydantic schemas for the System Settings module API contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.system_settings.models import (
    SystemSettingChangeAction,
    SystemSettingDefaultStatus,
    SystemSettingStatus,
    SystemSettingValueType,
)

SystemSettingValue = dict[str, Any] | list[Any] | str | int | float | bool | None


class SystemSettingsHealthRead(BaseModel):
    """System Settings module health response."""

    status: str
    module: str | None = None
    repositories: dict[str, bool] | None = None


class SystemSettingBase(BaseModel):
    """Shared fields for persisted configurable application settings."""

    category: str = Field(..., min_length=1, max_length=120)
    key: str = Field(..., min_length=1, max_length=160)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    value: SystemSettingValue = None
    default_value: SystemSettingValue = None
    value_type: SystemSettingValueType = SystemSettingValueType.STRING
    validation_rules: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    status: SystemSettingStatus = SystemSettingStatus.DRAFT
    created_by_id: int | None = None
    updated_by_id: int | None = None
    deleted_by_id: int | None = None


class SystemSettingCreate(SystemSettingBase):
    """Payload for creating a persisted configurable application setting."""


class SystemSettingUpdate(BaseModel):
    """Payload for partially updating a persisted system setting."""

    category: str | None = Field(default=None, min_length=1, max_length=120)
    key: str | None = Field(default=None, min_length=1, max_length=160)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    value: SystemSettingValue = None
    default_value: SystemSettingValue = None
    value_type: SystemSettingValueType | None = None
    validation_rules: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    status: SystemSettingStatus | None = None
    updated_by_id: int | None = None
    deleted_by_id: int | None = None


class SystemSettingRead(SystemSettingBase):
    """Response schema for a persisted configurable application setting."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class SystemSettingListResponse(BaseModel):
    """Paginated persisted system settings response."""

    items: list[SystemSettingRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class SystemSettingCountResponse(BaseModel):
    """Count response for persisted system settings."""

    total: int


class SystemSettingDefaultBase(BaseModel):
    """Shared fields for system setting default definitions."""

    category: str = Field(..., min_length=1, max_length=120)
    key: str = Field(..., min_length=1, max_length=160)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    default_value: SystemSettingValue = None
    value_type: SystemSettingValueType = SystemSettingValueType.STRING
    validation_rules: dict[str, Any] | None = None
    status: SystemSettingDefaultStatus = SystemSettingDefaultStatus.ACTIVE
    metadata_json: dict[str, Any] | None = None


class SystemSettingDefaultCreate(SystemSettingDefaultBase):
    """Payload for creating a system setting default definition."""


class SystemSettingDefaultUpdate(BaseModel):
    """Payload for partially updating a system setting default definition."""

    category: str | None = Field(default=None, min_length=1, max_length=120)
    key: str | None = Field(default=None, min_length=1, max_length=160)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    default_value: SystemSettingValue = None
    value_type: SystemSettingValueType | None = None
    validation_rules: dict[str, Any] | None = None
    status: SystemSettingDefaultStatus | None = None
    metadata_json: dict[str, Any] | None = None


class SystemSettingDefaultRead(SystemSettingDefaultBase):
    """Response schema for a system setting default definition."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class SystemSettingDefaultListResponse(BaseModel):
    """Paginated system setting defaults response."""

    items: list[SystemSettingDefaultRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class SystemSettingDefaultCountResponse(BaseModel):
    """Count response for system setting default definitions."""

    total: int


class SystemSettingChangeEventBase(BaseModel):
    """Shared fields for append-only system setting change events."""

    system_setting_id: int | None = None
    category: str = Field(..., min_length=1, max_length=120)
    key: str = Field(..., min_length=1, max_length=160)
    action: SystemSettingChangeAction
    old_value: SystemSettingValue = None
    new_value: SystemSettingValue = None
    actor_user_id: int | None = None
    reason: str | None = None
    source: str | None = Field(default=None, max_length=120)
    request_id: str | None = Field(default=None, max_length=120)
    correlation_id: str | None = Field(default=None, max_length=120)
    metadata_json: dict[str, Any] | None = None


class SystemSettingChangeEventCreate(SystemSettingChangeEventBase):
    """Payload for creating a system setting change event."""


class SystemSettingChangeEventRead(SystemSettingChangeEventBase):
    """Response schema for an append-only system setting change event."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    event_uuid: UUID
    created_at: datetime


class SystemSettingChangeEventListResponse(BaseModel):
    """Paginated system setting change events response."""

    items: list[SystemSettingChangeEventRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class SystemSettingChangeEventCountResponse(BaseModel):
    """Count response for system setting change events."""

    total: int


SystemSettingAuditEventCreate = SystemSettingChangeEventCreate
SystemSettingAuditEventRead = SystemSettingChangeEventRead
SystemSettingAuditEventListResponse = SystemSettingChangeEventListResponse
SystemSettingAuditEventCountResponse = SystemSettingChangeEventCountResponse


__all__ = [
    "SystemSettingAuditEventCountResponse",
    "SystemSettingAuditEventCreate",
    "SystemSettingAuditEventListResponse",
    "SystemSettingAuditEventRead",
    "SystemSettingChangeEventCountResponse",
    "SystemSettingChangeEventCreate",
    "SystemSettingChangeEventListResponse",
    "SystemSettingChangeEventRead",
    "SystemSettingCountResponse",
    "SystemSettingCreate",
    "SystemSettingDefaultCountResponse",
    "SystemSettingDefaultCreate",
    "SystemSettingDefaultListResponse",
    "SystemSettingDefaultRead",
    "SystemSettingDefaultUpdate",
    "SystemSettingListResponse",
    "SystemSettingRead",
    "SystemSettingUpdate",
    "SystemSettingValue",
    "SystemSettingsHealthRead",
]
