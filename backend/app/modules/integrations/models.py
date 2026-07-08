"""Domain models for the Integrations module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


json_type = JSONB().with_variant(JSON(), "sqlite")


class IntegrationProviderStatus(str, Enum):
    """Lifecycle states for integration provider definitions."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class IntegrationConnectionStatus(str, Enum):
    """Lifecycle states for configured integration connections."""

    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
    ARCHIVED = "archived"


class IntegrationSyncJobStatus(str, Enum):
    """Execution states for integration synchronization jobs."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IntegrationEventStatus(str, Enum):
    """Processing states for integration event records."""

    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"


class IntegrationProvider(Base):
    """External integration provider definition and capability metadata."""

    __tablename__ = "integration_providers"
    __table_args__ = (
        UniqueConstraint("code", name="uq_integration_providers_code"),
        Index("ix_integration_providers_code", "code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    code: Mapped[str] = mapped_column(String(length=120), nullable=False)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_type: Mapped[str] = mapped_column(String(length=80), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=IntegrationProviderStatus.ACTIVE.value,
        index=True,
    )

    auth_type: Mapped[str | None] = mapped_column(String(length=80), nullable=True, index=True)
    base_url: Mapped[str | None] = mapped_column(String(length=1024), nullable=True)
    capabilities: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    default_config: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
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

    connections: Mapped[list[IntegrationConnection]] = relationship(back_populates="provider")

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.provider_uuid


class IntegrationConnection(Base):
    """Configured tenant or system connection to an integration provider."""

    __tablename__ = "integration_connections"
    __table_args__ = (
        UniqueConstraint("provider_id", "name", name="uq_integration_connections_provider_name"),
        Index(
            "ix_integration_connections_uuid_name_provider",
            "connection_uuid",
            "name",
            "provider_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    connection_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("integration_providers.id"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(length=255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=IntegrationConnectionStatus.DRAFT.value,
        index=True,
    )
    environment: Mapped[str | None] = mapped_column(String(length=80), nullable=True, index=True)
    external_account_id: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True, index=True
    )

    config: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    credentials_ref: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    sync_settings: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
        nullable=True,
    )

    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    last_error_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    deleted_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
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

    provider: Mapped[IntegrationProvider] = relationship(back_populates="connections")
    sync_jobs: Mapped[list[IntegrationSyncJob]] = relationship(back_populates="connection")
    events: Mapped[list[IntegrationEvent]] = relationship(back_populates="connection")

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.connection_uuid


class IntegrationSyncJob(Base):
    """Single synchronization attempt for an integration connection."""

    __tablename__ = "integration_sync_jobs"
    __table_args__ = (
        Index("ix_integration_sync_jobs_connection_status", "connection_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )
    connection_id: Mapped[int] = mapped_column(
        ForeignKey("integration_connections.id"), nullable=False, index=True
    )

    sync_type: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    direction: Mapped[str | None] = mapped_column(String(length=40), nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=IntegrationSyncJobStatus.QUEUED.value,
        index=True,
    )

    request_payload: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    result_summary: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    records_processed: Mapped[int] = mapped_column(nullable=False, default=0)
    records_succeeded: Mapped[int] = mapped_column(nullable=False, default=0)
    records_failed: Mapped[int] = mapped_column(nullable=False, default=0)

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    triggered_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
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

    connection: Mapped[IntegrationConnection] = relationship(back_populates="sync_jobs")
    events: Mapped[list[IntegrationEvent]] = relationship(back_populates="sync_job")

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.job_uuid


class IntegrationEvent(Base):
    """Webhook, API, or internal event received from an integration connection."""

    __tablename__ = "integration_events"
    __table_args__ = (
        Index("ix_integration_events_connection_event_type", "connection_id", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )
    connection_id: Mapped[int] = mapped_column(
        ForeignKey("integration_connections.id"), nullable=False, index=True
    )
    sync_job_id: Mapped[int | None] = mapped_column(
        ForeignKey("integration_sync_jobs.id"), nullable=True, index=True
    )

    event_type: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=IntegrationEventStatus.RECEIVED.value,
        index=True,
    )
    source: Mapped[str | None] = mapped_column(String(length=120), nullable=True, index=True)
    external_event_id: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True, index=True
    )
    entity_type: Mapped[str | None] = mapped_column(String(length=120), nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(length=120), nullable=True, index=True)

    payload: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    headers: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    processing_result: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    connection: Mapped[IntegrationConnection] = relationship(back_populates="events")
    sync_job: Mapped[IntegrationSyncJob | None] = relationship(back_populates="events")

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.event_uuid


__all__ = [
    "IntegrationConnection",
    "IntegrationConnectionStatus",
    "IntegrationEvent",
    "IntegrationEventStatus",
    "IntegrationProvider",
    "IntegrationProviderStatus",
    "IntegrationSyncJob",
    "IntegrationSyncJobStatus",
]
