"""Pydantic schemas for the Reporting & Analytics module."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.reporting_analytics.models import (
    AnalyticsSnapshotPeriod,
    AnalyticsSnapshotStatus,
    DashboardStatus,
    ReportDefinitionStatus,
    ReportOutputFormat,
    ReportRunStatus,
)


class ReportingAnalyticsHealthResponse(BaseModel):
    """Health response for the Reporting & Analytics module."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    module: str


class DashboardDefinitionBase(BaseModel):
    """Shared dashboard definition fields."""

    code: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=120)
    status: DashboardStatus = DashboardStatus.DRAFT
    owner_user_id: int | None = None
    layout_config: dict[str, Any] | None = None
    widget_config: dict[str, Any] | None = None
    filter_config: dict[str, Any] | None = None


class DashboardDefinitionCreate(DashboardDefinitionBase):
    """Create payload for dashboard definitions."""


class DashboardDefinitionUpdate(BaseModel):
    """Update payload for dashboard definitions."""

    code: str | None = Field(default=None, min_length=1, max_length=120)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=120)
    status: DashboardStatus | None = None
    owner_user_id: int | None = None
    layout_config: dict[str, Any] | None = None
    widget_config: dict[str, Any] | None = None
    filter_config: dict[str, Any] | None = None


class DashboardDefinitionResponse(DashboardDefinitionBase):
    """Response schema for dashboard definitions."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    dashboard_uuid: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class DashboardDefinitionListResponse(BaseModel):
    """Paginated dashboard definition response."""

    items: list[DashboardDefinitionResponse]
    total: int
    limit: int | None = None
    offset: int | None = None


class ReportDefinitionBase(BaseModel):
    """Shared report definition fields."""

    code: str = Field(..., min_length=1, max_length=120)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=120)
    source_module: str | None = Field(default=None, max_length=120)
    status: ReportDefinitionStatus = ReportDefinitionStatus.DRAFT
    default_format: ReportOutputFormat = ReportOutputFormat.PDF
    owner_user_id: int | None = None
    query_config: dict[str, Any] | None = None
    filter_schema: dict[str, Any] | None = None
    layout_config: dict[str, Any] | None = None


class ReportDefinitionCreate(ReportDefinitionBase):
    """Create payload for report definitions."""


class ReportDefinitionUpdate(BaseModel):
    """Update payload for report definitions."""

    code: str | None = Field(default=None, min_length=1, max_length=120)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=120)
    source_module: str | None = Field(default=None, max_length=120)
    status: ReportDefinitionStatus | None = None
    default_format: ReportOutputFormat | None = None
    owner_user_id: int | None = None
    query_config: dict[str, Any] | None = None
    filter_schema: dict[str, Any] | None = None
    layout_config: dict[str, Any] | None = None
    last_generated_at: datetime | None = None


class ReportDefinitionResponse(ReportDefinitionBase):
    """Response schema for report definitions."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    report_uuid: UUID
    last_generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ReportDefinitionListResponse(BaseModel):
    """Paginated report definition response."""

    items: list[ReportDefinitionResponse]
    total: int
    limit: int | None = None
    offset: int | None = None


class ReportRunBase(BaseModel):
    """Shared report run fields."""

    report_definition_id: int
    requested_by_user_id: int | None = None
    file_object_id: int | None = None
    status: ReportRunStatus = ReportRunStatus.QUEUED
    output_format: ReportOutputFormat = ReportOutputFormat.PDF
    parameters: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    row_count: int = Field(default=0, ge=0)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None


class ReportRunCreate(ReportRunBase):
    """Create payload for report runs."""


class ReportRunUpdate(BaseModel):
    """Update payload for report runs."""

    requested_by_user_id: int | None = None
    file_object_id: int | None = None
    status: ReportRunStatus | None = None
    output_format: ReportOutputFormat | None = None
    parameters: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    row_count: int | None = Field(default=None, ge=0)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    failure_reason: str | None = None


class ReportRunResponse(ReportRunBase):
    """Response schema for report runs."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    run_uuid: UUID
    created_at: datetime
    updated_at: datetime


class ReportRunListResponse(BaseModel):
    """Paginated report run response."""

    items: list[ReportRunResponse]
    total: int
    limit: int | None = None
    offset: int | None = None


class AnalyticsSnapshotBase(BaseModel):
    """Shared analytics snapshot fields."""

    metric_key: str = Field(..., min_length=1, max_length=160)
    metric_name: str = Field(..., min_length=1, max_length=255)
    source_module: str | None = Field(default=None, max_length=120)
    entity_type: str | None = Field(default=None, max_length=120)
    entity_id: str | None = Field(default=None, max_length=120)
    period: AnalyticsSnapshotPeriod = AnalyticsSnapshotPeriod.DAILY
    status: AnalyticsSnapshotStatus = AnalyticsSnapshotStatus.READY
    value: dict[str, Any] = Field(default_factory=dict)
    dimensions: dict[str, Any] | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    failure_reason: str | None = None


class AnalyticsSnapshotCreate(AnalyticsSnapshotBase):
    """Create payload for analytics snapshots."""


class AnalyticsSnapshotUpdate(BaseModel):
    """Update payload for analytics snapshots."""

    metric_key: str | None = Field(default=None, min_length=1, max_length=160)
    metric_name: str | None = Field(default=None, min_length=1, max_length=255)
    source_module: str | None = Field(default=None, max_length=120)
    entity_type: str | None = Field(default=None, max_length=120)
    entity_id: str | None = Field(default=None, max_length=120)
    period: AnalyticsSnapshotPeriod | None = None
    status: AnalyticsSnapshotStatus | None = None
    value: dict[str, Any] | None = None
    dimensions: dict[str, Any] | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    calculated_at: datetime | None = None
    failure_reason: str | None = None


class AnalyticsSnapshotResponse(AnalyticsSnapshotBase):
    """Response schema for analytics snapshots."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    snapshot_uuid: UUID
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime


class AnalyticsSnapshotListResponse(BaseModel):
    """Paginated analytics snapshot response."""

    items: list[AnalyticsSnapshotResponse]
    total: int
    limit: int | None = None
    offset: int | None = None


__all__ = [
    "AnalyticsSnapshotCreate",
    "AnalyticsSnapshotListResponse",
    "AnalyticsSnapshotResponse",
    "AnalyticsSnapshotUpdate",
    "DashboardDefinitionCreate",
    "DashboardDefinitionListResponse",
    "DashboardDefinitionResponse",
    "DashboardDefinitionUpdate",
    "ReportDefinitionCreate",
    "ReportDefinitionListResponse",
    "ReportDefinitionResponse",
    "ReportDefinitionUpdate",
    "ReportingAnalyticsHealthResponse",
    "ReportRunCreate",
    "ReportRunListResponse",
    "ReportRunResponse",
    "ReportRunUpdate",
]
