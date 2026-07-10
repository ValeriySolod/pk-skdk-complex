"""Pydantic schemas for the Monitoring & Health module API contract."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .models import (HealthCheckStatus, MonitoringMetricCategory,
                     SystemIncidentSeverity, SystemIncidentStatus)


class MonitoringHealthHealthRead(BaseModel):
    status: str
    module: str


class HealthCheckCreate(BaseModel):
    component: str = Field(min_length=1, max_length=120)
    status: HealthCheckStatus = HealthCheckStatus.UNKNOWN
    response_time_ms: float | None = Field(default=None, ge=0)
    message: str | None = None
    details: Any | None = None
    checked_at: datetime | None = None


class HealthCheckUpdate(BaseModel):
    component: str | None = Field(default=None, min_length=1, max_length=120)
    status: HealthCheckStatus | None = None
    response_time_ms: float | None = Field(default=None, ge=0)
    message: str | None = None
    details: Any | None = None
    checked_at: datetime | None = None


class HealthCheckStatusUpdate(BaseModel):
    status: HealthCheckStatus


class HealthCheckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    record_uuid: UUID
    component: str
    status: HealthCheckStatus
    response_time_ms: float | None
    message: str | None
    details: Any | None
    checked_at: datetime
    created_at: datetime


class MonitoringMetricCreate(BaseModel):
    metric_name: str = Field(min_length=1, max_length=160)
    category: MonitoringMetricCategory = MonitoringMetricCategory.CUSTOM
    source: str | None = Field(default=None, max_length=120)
    value: float
    unit: str | None = Field(default=None, max_length=40)
    labels: Any | None = None
    details: Any | None = None
    recorded_at: datetime | None = None


class MonitoringMetricUpdate(BaseModel):
    metric_name: str | None = Field(default=None, min_length=1, max_length=160)
    category: MonitoringMetricCategory | None = None
    source: str | None = Field(default=None, max_length=120)
    value: float | None = None
    unit: str | None = Field(default=None, max_length=40)
    labels: Any | None = None
    details: Any | None = None
    recorded_at: datetime | None = None


class MonitoringMetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    metric_uuid: UUID
    metric_name: str
    category: MonitoringMetricCategory
    source: str | None
    value: float
    unit: str | None
    labels: Any | None
    details: Any | None
    recorded_at: datetime
    created_at: datetime


class SystemIncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    severity: SystemIncidentSeverity = SystemIncidentSeverity.MEDIUM
    status: SystemIncidentStatus = SystemIncidentStatus.OPEN
    source: str | None = Field(default=None, max_length=120)
    component: str | None = Field(default=None, max_length=120)
    description: str | None = None
    resolution_summary: str | None = None
    metadata_json: Any | None = None
    detected_at: datetime | None = None
    resolved_at: datetime | None = None


class SystemIncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    severity: SystemIncidentSeverity | None = None
    status: SystemIncidentStatus | None = None
    source: str | None = Field(default=None, max_length=120)
    component: str | None = Field(default=None, max_length=120)
    description: str | None = None
    resolution_summary: str | None = None
    metadata_json: Any | None = None
    detected_at: datetime | None = None
    resolved_at: datetime | None = None


class SystemIncidentStatusUpdate(BaseModel):
    status: SystemIncidentStatus
    resolution_summary: str | None = None
    resolved_at: datetime | None = None


class SystemIncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    incident_uuid: UUID
    title: str
    severity: SystemIncidentSeverity
    status: SystemIncidentStatus
    source: str | None
    component: str | None
    description: str | None
    resolution_summary: str | None
    metadata_json: Any | None
    detected_at: datetime
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class HealthCheckListResponse(BaseModel):
    items: list[HealthCheckRead]; total: int; limit: int; offset: int

class MonitoringMetricListResponse(BaseModel):
    items: list[MonitoringMetricRead]; total: int; limit: int; offset: int

class SystemIncidentListResponse(BaseModel):
    items: list[SystemIncidentRead]; total: int; limit: int; offset: int


class HealthCheckFilterParams(BaseModel):
    component: str | None = None
    status: HealthCheckStatus | None = None
    checked_from: datetime | None = None; checked_to: datetime | None = None
    created_from: datetime | None = None; created_to: datetime | None = None
    search: str | None = None
    limit: int = Field(default=100, ge=1, le=500); offset: int = Field(default=0, ge=0)

class MonitoringMetricFilterParams(BaseModel):
    metric_name: str | None = None; category: MonitoringMetricCategory | None = None
    source: str | None = None; unit: str | None = None
    recorded_from: datetime | None = None; recorded_to: datetime | None = None
    created_from: datetime | None = None; created_to: datetime | None = None
    search: str | None = None
    limit: int = Field(default=100, ge=1, le=500); offset: int = Field(default=0, ge=0)

class SystemIncidentFilterParams(BaseModel):
    title: str | None = None; severity: SystemIncidentSeverity | None = None
    status: SystemIncidentStatus | None = None; source: str | None = None; component: str | None = None
    detected_from: datetime | None = None; detected_to: datetime | None = None
    resolved_from: datetime | None = None; resolved_to: datetime | None = None
    created_from: datetime | None = None; created_to: datetime | None = None
    search: str | None = None
    limit: int = Field(default=100, ge=1, le=500); offset: int = Field(default=0, ge=0)

# Stable compatibility aliases.
HealthCheckRecordCreate = HealthCheckCreate
HealthCheckRecordUpdate = HealthCheckUpdate
HealthCheckRecordRead = HealthCheckRead
HealthCheckRecordListResponse = HealthCheckListResponse
