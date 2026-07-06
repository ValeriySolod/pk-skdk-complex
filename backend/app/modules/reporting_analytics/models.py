"""Domain models for the Reporting & Analytics module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DashboardStatus(str, Enum):
    """Lifecycle states for dashboard definitions."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ReportDefinitionStatus(str, Enum):
    """Lifecycle states for report definitions."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ReportRunStatus(str, Enum):
    """Lifecycle states for report generation runs."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReportOutputFormat(str, Enum):
    """Output formats supported by generated reports."""

    PDF = "pdf"
    XLSX = "xlsx"
    CSV = "csv"
    HTML = "html"
    JSON = "json"


class AnalyticsSnapshotPeriod(str, Enum):
    """Aggregation windows for analytics snapshots."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class AnalyticsSnapshotStatus(str, Enum):
    """Lifecycle states for analytics snapshot records."""

    READY = "ready"
    STALE = "stale"
    FAILED = "failed"


class DashboardDefinition(Base):
    """Dashboard layout and widget configuration."""

    __tablename__ = "analytics_dashboard_definitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    dashboard_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    code: Mapped[str] = mapped_column(String(length=120), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=DashboardStatus.DRAFT.value,
        index=True,
    )
    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    layout_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    widget_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    filter_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )


class ReportDefinition(Base):
    """Reusable report definition and generation configuration."""

    __tablename__ = "analytics_report_definitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    code: Mapped[str] = mapped_column(String(length=120), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    source_module: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=ReportDefinitionStatus.DRAFT.value,
        index=True,
    )
    default_format: Mapped[str] = mapped_column(
        String(length=20),
        nullable=False,
        default=ReportOutputFormat.PDF.value,
        index=True,
    )
    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    query_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    filter_schema: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    layout_config: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )

    last_generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )


class ReportRun(Base):
    """Single execution attempt for a report definition."""

    __tablename__ = "analytics_report_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )
    report_definition_id: Mapped[int] = mapped_column(
        ForeignKey("analytics_report_definitions.id"), nullable=False, index=True
    )
    requested_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    file_object_id: Mapped[int | None] = mapped_column(
        ForeignKey("file_storage_objects.id"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=ReportRunStatus.QUEUED.value,
        index=True,
    )
    output_format: Mapped[str] = mapped_column(
        String(length=20),
        nullable=False,
        default=ReportOutputFormat.PDF.value,
        index=True,
    )
    parameters: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    result_summary: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    row_count: Mapped[int] = mapped_column(nullable=False, default=0)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class AnalyticsSnapshot(Base):
    """Materialized analytics metric snapshot for dashboards and reports."""

    __tablename__ = "analytics_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    metric_key: Mapped[str] = mapped_column(String(length=160), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    source_module: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    entity_type: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    entity_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )

    period: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=AnalyticsSnapshotPeriod.DAILY.value,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=AnalyticsSnapshotStatus.READY.value,
        index=True,
    )
    value: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
    )
    dimensions: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )

    period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "AnalyticsSnapshot",
    "AnalyticsSnapshotPeriod",
    "AnalyticsSnapshotStatus",
    "DashboardDefinition",
    "DashboardStatus",
    "ReportDefinition",
    "ReportDefinitionStatus",
    "ReportOutputFormat",
    "ReportRun",
    "ReportRunStatus",
]
