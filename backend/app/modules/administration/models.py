"""Domain models for the Administration module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AdministrationReferenceStatus(str, Enum):
    """Lifecycle states for administrated reference/catalog entries."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class MaintenanceTaskStatus(str, Enum):
    """Lifecycle states for administrative maintenance tasks."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AdminActionStatus(str, Enum):
    """Outcome states for administrative action records."""

    SUCCESS = "success"
    FAILED = "failed"
    DENIED = "denied"


class AdministrationReference(Base):
    """Configurable reference/catalog entry managed by administrators."""

    __tablename__ = "administration_references"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    catalog: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(length=120), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=AdministrationReferenceStatus.DRAFT.value,
        index=True,
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
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


class MaintenanceTask(Base):
    """Administrative maintenance operation request and execution result."""

    __tablename__ = "administration_maintenance_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    operation_type: Mapped[str] = mapped_column(
        String(length=120), nullable=False, index=True
    )
    operation_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=MaintenanceTaskStatus.QUEUED.value,
        index=True,
    )

    requested_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    result: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
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


class AdminActionEvent(Base):
    """Lightweight audit-oriented record of an administrative action."""

    __tablename__ = "administration_action_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    action_type: Mapped[str] = mapped_column(
        String(length=120), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=AdminActionStatus.SUCCESS.value,
        index=True,
    )
    target_type: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    target_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    resource: Mapped[str | None] = mapped_column(String(length=255), nullable=True)

    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    actor_username: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    request_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )


__all__ = [
    "AdminActionEvent",
    "AdminActionStatus",
    "AdministrationReference",
    "AdministrationReferenceStatus",
    "MaintenanceTask",
    "MaintenanceTaskStatus",
]
