"""Pydantic schemas for the Integrations module API contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.integrations.models import (
    IntegrationConnectionStatus,
    IntegrationEventStatus,
    IntegrationProviderStatus,
    IntegrationSyncJobStatus,
)


class IntegrationsHealthRead(BaseModel):
    """Integrations module health response."""

    status: str
    module: str


class IntegrationProviderBase(BaseModel):
    """Shared integration provider fields."""

    code: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    provider_type: str = Field(..., min_length=1, max_length=80)
    status: IntegrationProviderStatus = IntegrationProviderStatus.ACTIVE
    auth_type: str | None = Field(default=None, max_length=80)
    base_url: str | None = Field(default=None, max_length=1024)
    capabilities: dict[str, Any] | None = None
    default_config: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None


class IntegrationProviderCreate(IntegrationProviderBase):
    """Payload for creating an integration provider definition."""


class IntegrationProviderUpdate(BaseModel):
    """Payload for partially updating an integration provider definition."""

    code: str | None = Field(default=None, min_length=1, max_length=120)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    provider_type: str | None = Field(default=None, min_length=1, max_length=80)
    status: IntegrationProviderStatus | None = None
    auth_type: str | None = Field(default=None, max_length=80)
    base_url: str | None = Field(default=None, max_length=1024)
    capabilities: dict[str, Any] | None = None
    default_config: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None


class IntegrationProviderRead(IntegrationProviderBase):
    """Response schema for an integration provider definition."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_uuid: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class IntegrationProviderListResponse(BaseModel):
    """Paginated integration provider response."""

    items: list[IntegrationProviderRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class IntegrationProviderFilterParams(BaseModel):
    """Query parameters for listing integration providers."""

    code: str | None = Field(default=None, max_length=120)
    provider_type: str | None = Field(default=None, max_length=80)
    status: IntegrationProviderStatus | None = None
    auth_type: str | None = Field(default=None, max_length=80)
    created_from: datetime | None = None
    created_to: datetime | None = None
    include_deleted: bool = False
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class IntegrationConnectionBase(BaseModel):
    """Shared integration connection fields."""

    provider_id: int = Field(ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: IntegrationConnectionStatus = IntegrationConnectionStatus.DRAFT
    environment: str | None = Field(default=None, max_length=80)
    external_account_id: str | None = Field(default=None, max_length=255)
    config: dict[str, Any] | None = None
    credentials_ref: str | None = Field(default=None, max_length=255)
    sync_settings: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    last_sync_at: datetime | None = None
    last_error_at: datetime | None = None
    last_error_message: str | None = None
    created_by_id: int | None = Field(default=None, ge=1)
    updated_by_id: int | None = Field(default=None, ge=1)
    deleted_by_id: int | None = Field(default=None, ge=1)


class IntegrationConnectionCreate(IntegrationConnectionBase):
    """Payload for creating an integration connection."""


class IntegrationConnectionUpdate(BaseModel):
    """Payload for partially updating an integration connection."""

    provider_id: int | None = Field(default=None, ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: IntegrationConnectionStatus | None = None
    environment: str | None = Field(default=None, max_length=80)
    external_account_id: str | None = Field(default=None, max_length=255)
    config: dict[str, Any] | None = None
    credentials_ref: str | None = Field(default=None, max_length=255)
    sync_settings: dict[str, Any] | None = None
    metadata_json: dict[str, Any] | None = None
    last_sync_at: datetime | None = None
    last_error_at: datetime | None = None
    last_error_message: str | None = None
    updated_by_id: int | None = Field(default=None, ge=1)
    deleted_by_id: int | None = Field(default=None, ge=1)


class IntegrationConnectionRead(IntegrationConnectionBase):
    """Response schema for an integration connection."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    connection_uuid: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class IntegrationConnectionListResponse(BaseModel):
    """Paginated integration connection response."""

    items: list[IntegrationConnectionRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class IntegrationConnectionFilterParams(BaseModel):
    """Query parameters for listing integration connections."""

    provider_id: int | None = Field(default=None, ge=1)
    name: str | None = Field(default=None, max_length=255)
    status: IntegrationConnectionStatus | None = None
    environment: str | None = Field(default=None, max_length=80)
    external_account_id: str | None = Field(default=None, max_length=255)
    created_by_id: int | None = Field(default=None, ge=1)
    updated_by_id: int | None = Field(default=None, ge=1)
    last_sync_from: datetime | None = None
    last_sync_to: datetime | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    include_deleted: bool = False
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class IntegrationSyncJobBase(BaseModel):
    """Shared integration sync job fields."""

    connection_id: int = Field(ge=1)
    sync_type: str = Field(..., min_length=1, max_length=120)
    direction: str | None = Field(default=None, max_length=40)
    status: IntegrationSyncJobStatus = IntegrationSyncJobStatus.QUEUED
    request_payload: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    records_processed: int = Field(default=0, ge=0)
    records_succeeded: int = Field(default=0, ge=0)
    records_failed: int = Field(default=0, ge=0)
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None
    triggered_by_user_id: int | None = Field(default=None, ge=1)
    correlation_id: str | None = Field(default=None, max_length=120)
    metadata_json: dict[str, Any] | None = None


class IntegrationSyncJobCreate(IntegrationSyncJobBase):
    """Payload for creating an integration sync job."""


class IntegrationSyncJobUpdate(BaseModel):
    """Payload for partially updating an integration sync job."""

    sync_type: str | None = Field(default=None, min_length=1, max_length=120)
    direction: str | None = Field(default=None, max_length=40)
    status: IntegrationSyncJobStatus | None = None
    request_payload: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    records_processed: int | None = Field(default=None, ge=0)
    records_succeeded: int | None = Field(default=None, ge=0)
    records_failed: int | None = Field(default=None, ge=0)
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None
    correlation_id: str | None = Field(default=None, max_length=120)
    metadata_json: dict[str, Any] | None = None


class IntegrationSyncJobRead(IntegrationSyncJobBase):
    """Response schema for an integration sync job."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_uuid: UUID
    created_at: datetime
    updated_at: datetime


class IntegrationSyncJobListResponse(BaseModel):
    """Paginated integration sync job response."""

    items: list[IntegrationSyncJobRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class IntegrationSyncJobFilterParams(BaseModel):
    """Query parameters for listing integration sync jobs."""

    connection_id: int | None = Field(default=None, ge=1)
    sync_type: str | None = Field(default=None, max_length=120)
    direction: str | None = Field(default=None, max_length=40)
    status: IntegrationSyncJobStatus | None = None
    triggered_by_user_id: int | None = Field(default=None, ge=1)
    correlation_id: str | None = Field(default=None, max_length=120)
    scheduled_from: datetime | None = None
    scheduled_to: datetime | None = None
    started_from: datetime | None = None
    started_to: datetime | None = None
    completed_from: datetime | None = None
    completed_to: datetime | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class IntegrationEventBase(BaseModel):
    """Shared integration event fields."""

    connection_id: int = Field(ge=1)
    sync_job_id: int | None = Field(default=None, ge=1)
    event_type: str = Field(..., min_length=1, max_length=120)
    status: IntegrationEventStatus = IntegrationEventStatus.RECEIVED
    source: str | None = Field(default=None, max_length=120)
    external_event_id: str | None = Field(default=None, max_length=255)
    entity_type: str | None = Field(default=None, max_length=120)
    entity_id: str | None = Field(default=None, max_length=120)
    payload: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
    processing_result: dict[str, Any] | None = None
    error_message: str | None = None
    received_at: datetime | None = None
    processed_at: datetime | None = None
    correlation_id: str | None = Field(default=None, max_length=120)
    metadata_json: dict[str, Any] | None = None


class IntegrationEventCreate(IntegrationEventBase):
    """Payload for creating an integration event."""


class IntegrationEventUpdate(BaseModel):
    """Payload for partially updating an integration event."""

    status: IntegrationEventStatus | None = None
    payload: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
    processing_result: dict[str, Any] | None = None
    error_message: str | None = None
    processed_at: datetime | None = None
    correlation_id: str | None = Field(default=None, max_length=120)
    metadata_json: dict[str, Any] | None = None


class IntegrationEventRead(IntegrationEventBase):
    """Response schema for an integration event."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    event_uuid: UUID
    received_at: datetime
    created_at: datetime


class IntegrationEventListResponse(BaseModel):
    """Paginated integration event response."""

    items: list[IntegrationEventRead]
    total: int
    limit: int | None = None
    offset: int | None = None


class IntegrationEventFilterParams(BaseModel):
    """Query parameters for listing integration events."""

    connection_id: int | None = Field(default=None, ge=1)
    sync_job_id: int | None = Field(default=None, ge=1)
    event_type: str | None = Field(default=None, max_length=120)
    status: IntegrationEventStatus | None = None
    source: str | None = Field(default=None, max_length=120)
    external_event_id: str | None = Field(default=None, max_length=255)
    entity_type: str | None = Field(default=None, max_length=120)
    entity_id: str | None = Field(default=None, max_length=120)
    correlation_id: str | None = Field(default=None, max_length=120)
    received_from: datetime | None = None
    received_to: datetime | None = None
    processed_from: datetime | None = None
    processed_to: datetime | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


IntegrationProviderResponse = IntegrationProviderRead
IntegrationConnectionResponse = IntegrationConnectionRead
IntegrationSyncJobResponse = IntegrationSyncJobRead
IntegrationEventResponse = IntegrationEventRead


__all__ = [
    "IntegrationConnectionCreate",
    "IntegrationConnectionFilterParams",
    "IntegrationConnectionListResponse",
    "IntegrationConnectionRead",
    "IntegrationConnectionResponse",
    "IntegrationConnectionUpdate",
    "IntegrationEventCreate",
    "IntegrationEventFilterParams",
    "IntegrationEventListResponse",
    "IntegrationEventRead",
    "IntegrationEventResponse",
    "IntegrationEventUpdate",
    "IntegrationProviderCreate",
    "IntegrationProviderFilterParams",
    "IntegrationProviderListResponse",
    "IntegrationProviderRead",
    "IntegrationProviderResponse",
    "IntegrationProviderUpdate",
    "IntegrationSyncJobCreate",
    "IntegrationSyncJobFilterParams",
    "IntegrationSyncJobListResponse",
    "IntegrationSyncJobRead",
    "IntegrationSyncJobResponse",
    "IntegrationSyncJobUpdate",
    "IntegrationsHealthRead",
]
