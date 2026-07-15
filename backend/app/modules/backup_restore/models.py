"""Domain models for the Backup & Restore module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, JSON, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


json_type = JSONB().with_variant(JSON(), "sqlite")


class BackupJobType(str, Enum):
    """Supported backup execution types."""

    FULL = "full"
    INCREMENTAL = "incremental"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class BackupJobStatus(str, Enum):
    """Lifecycle states for backup job execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RestoreJobStatus(str, Enum):
    """Lifecycle states for restore job execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackupJob(Base):
    """Backup creation request, execution state, and artifact metadata."""

    __tablename__ = "backup_jobs"
    __table_args__ = (
        Index("ix_backup_jobs_type_status", "backup_type", "status"),
        Index("ix_backup_jobs_storage_artifact", "storage_location", "artifact_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    title: Mapped[str] = mapped_column(String(length=255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    backup_type: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=BackupJobType.MANUAL.value,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=BackupJobStatus.PENDING.value,
        index=True,
    )

    storage_location: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True, index=True
    )
    storage_path: Mapped[str | None] = mapped_column(String(length=1024), nullable=True)
    artifact_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(length=128), nullable=True, index=True)

    config: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    result_summary: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
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

    restore_jobs: Mapped[list[RestoreJob]] = relationship(back_populates="backup_job")

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.job_uuid


class RestoreJob(Base):
    """Restore workflow request and execution state."""

    __tablename__ = "restore_jobs"
    __table_args__ = (
        Index("ix_restore_jobs_backup_status", "backup_job_id", "status"),
        Index("ix_restore_jobs_scope_status", "restore_scope", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    job_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )
    backup_job_id: Mapped[int | None] = mapped_column(
        ForeignKey("backup_jobs.id"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(length=255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=RestoreJobStatus.PENDING.value,
        index=True,
    )
    restore_scope: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    target_environment: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )

    source_artifact_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    source_storage_path: Mapped[str | None] = mapped_column(String(length=1024), nullable=True)
    config: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    result_summary: Mapped[dict[str, Any] | None] = mapped_column(json_type, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
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

    backup_job: Mapped[BackupJob | None] = relationship(back_populates="restore_jobs")

    @property
    def uuid(self) -> UUID:
        """Compatibility API UUID alias."""
        return self.job_uuid


__all__ = [
    "BackupJob",
    "BackupJobStatus",
    "BackupJobType",
    "RestoreJob",
    "RestoreJobStatus",
]
