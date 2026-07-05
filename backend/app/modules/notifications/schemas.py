from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.notifications.models import (
    NotificationChannel,
    NotificationDeliveryStatus,
    NotificationPriority,
    NotificationProvider,
    NotificationStatus,
    NotificationType,
)


class NotificationsHealthRead(BaseModel):
    status: str


class NotificationBase(BaseModel):
    recipient_user_id: int | None = Field(default=None, ge=1)
    actor_user_id: int | None = Field(default=None, ge=1)
    type: str = NotificationType.SYSTEM.value
    channel: str = NotificationChannel.IN_APP.value
    priority: str = NotificationPriority.NORMAL.value
    status: str = NotificationStatus.PENDING.value
    title: str = Field(min_length=1, max_length=255)
    body: str | None = None
    payload: dict[str, Any] | None = None
    entity_type: str | None = Field(default=None, max_length=120)
    entity_id: str | None = Field(default=None, max_length=120)
    correlation_id: str | None = Field(default=None, max_length=120)
    request_id: str | None = Field(default=None, max_length=120)
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    dismissed_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    recipient_user_id: int | None = Field(default=None, ge=1)
    actor_user_id: int | None = Field(default=None, ge=1)
    type: str | None = None
    channel: str | None = None
    priority: str | None = None
    status: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    body: str | None = None
    payload: dict[str, Any] | None = None
    entity_type: str | None = Field(default=None, max_length=120)
    entity_id: str | None = Field(default=None, max_length=120)
    correlation_id: str | None = Field(default=None, max_length=120)
    request_id: str | None = Field(default=None, max_length=120)
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    dismissed_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None


class NotificationRead(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    notification_uuid: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class NotificationListResponse(BaseModel):
    items: list[NotificationRead]
    total: int
    limit: int
    offset: int


class NotificationFilterParams(BaseModel):
    recipient_user_id: int | None = Field(default=None, ge=1)
    actor_user_id: int | None = Field(default=None, ge=1)
    type: str | None = None
    channel: str | None = None
    priority: str | None = None
    status: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    correlation_id: str | None = None
    request_id: str | None = None
    scheduled_from: datetime | None = None
    scheduled_to: datetime | None = None
    sent_from: datetime | None = None
    sent_to: datetime | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    include_deleted: bool = False
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class NotificationDeliveryBase(BaseModel):
    notification_id: int = Field(ge=1)
    channel: str = NotificationChannel.IN_APP.value
    provider: str | None = NotificationProvider.INTERNAL.value
    provider_message_id: str | None = Field(default=None, max_length=255)
    status: str = NotificationDeliveryStatus.PENDING.value
    attempt_count: int = Field(default=0, ge=0)
    last_attempt_at: datetime | None = None
    delivered_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None
    provider_response: dict[str, Any] | None = None


class NotificationDeliveryCreate(NotificationDeliveryBase):
    pass


class NotificationDeliveryUpdate(BaseModel):
    notification_id: int | None = Field(default=None, ge=1)
    channel: str | None = None
    provider: str | None = None
    provider_message_id: str | None = Field(default=None, max_length=255)
    status: str | None = None
    attempt_count: int | None = Field(default=None, ge=0)
    last_attempt_at: datetime | None = None
    delivered_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None
    provider_response: dict[str, Any] | None = None


class NotificationDeliveryRead(NotificationDeliveryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    delivery_uuid: UUID
    created_at: datetime
    updated_at: datetime


class NotificationDeliveryListResponse(BaseModel):
    items: list[NotificationDeliveryRead]
    total: int
    limit: int
    offset: int


class NotificationDeliveryFilterParams(BaseModel):
    notification_id: int | None = Field(default=None, ge=1)
    channel: str | None = None
    provider: str | None = None
    provider_message_id: str | None = None
    status: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    last_attempt_from: datetime | None = None
    last_attempt_to: datetime | None = None
    delivered_from: datetime | None = None
    delivered_to: datetime | None = None
    failed_from: datetime | None = None
    failed_to: datetime | None = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


NotificationResponse = NotificationRead
NotificationDeliveryResponse = NotificationDeliveryRead
