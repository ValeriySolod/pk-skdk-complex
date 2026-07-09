"""Domain models for the Monitoring & Health module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, Index, JSON, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


json_type = JSONB().with_variant(JSON(), "sqlite")


class HealthCheckStatus(str, Enum):
    """Execution states for health check records."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MonitoringMetricCategory(str, Enum):
    """Common metric categories."""

    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class SystemIncidentSeverity(str, Enum):
    """Severity levels for operational incidents."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SystemIncidentStatus(str, Enum):
    """Lifecycle states for operational incidents."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class HealthCheckRecord(Base):
    """Recorded health check execution for an application component."""

    __tablename__ = "health_check_records"
    __table_args__ = (
        Index("ix_health_check_records_component_status", "component", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    record_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    component: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=HealthCheckStatus.UNKNOWN.value,
        index=True,
    )
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.record_uuid


class MonitoringMetric(Base):
    """Metric sample recorded from a system, application, or integration source."""

    __tablename__ = "monitoring_metrics"
    __table_args__ = (
        Index("ix_monitoring_metrics_name_recorded_at", "metric_name", "recorded_at"),
        Index("ix_monitoring_metrics_category_source", "category", "source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    metric_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    metric_name: Mapped[str] = mapped_column(String(length=160), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(length=80),
        nullable=False,
        default=MonitoringMetricCategory.CUSTOM.value,
        index=True,
    )
    source: Mapped[str | None] = mapped_column(String(length=120), nullable=True, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(length=40), nullable=True)
    labels: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.metric_uuid


class SystemIncident(Base):
    """Operational incident tracked through investigation and resolution."""

    __tablename__ = "system_incidents"
    __table_args__ = (
        Index("ix_system_incidents_severity_status", "severity", "status"),
        Index("ix_system_incidents_source_status", "source", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    title: Mapped[str] = mapped_column(String(length=255), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=SystemIncidentSeverity.MEDIUM.value,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=SystemIncidentStatus.OPEN.value,
        index=True,
    )
    source: Mapped[str | None] = mapped_column(String(length=120), nullable=True, index=True)
    component: Mapped[str | None] = mapped_column(String(length=120), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
        nullable=True,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
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

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.incident_uuid


__all__ = [
    "HealthCheckRecord",
    "HealthCheckStatus",
    "MonitoringMetric",
    "MonitoringMetricCategory",
    "SystemIncident",
    "SystemIncidentSeverity",
    "SystemIncidentStatus",
]
