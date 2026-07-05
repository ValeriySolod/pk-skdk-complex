from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditLogHealthRead(BaseModel):
    status: str


class AuditLogBase(BaseModel):
    event_type: str
    entity_type: str | None = None
    entity_id: str | None = None
    actor_user_id: int | None = None
    actor_username: str | None = None
    action: str
    status: str = "success"
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_uuid: UUID
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogRead]
    total: int
    limit: int
    offset: int


class AuditLogFilterParams(BaseModel):
    actor_user_id: int | None = None
    actor_username: str | None = None
    event_type: str | None = None
    action: str | None = None
    status: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


AuditLogResponse = AuditLogRead
