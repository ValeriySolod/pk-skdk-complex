"""Domain models for the notifications module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class NotificationStatus(str, Enum):
    """Lifecycle states for notifications."""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    READ = "read"
    DISMISSED = "dismissed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationChannel(str, Enum):
    """Delivery channels supported by the notifications module."""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Priority levels for notification processing and display."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(str, Enum):
    """High-level notification categories."""

    SYSTEM = "system"
    SECURITY = "security"
    ACCOUNT = "account"
    WORKFLOW = "workflow"
    REMINDER = "reminder"
    ALERT = "alert"


class NotificationDeliveryStatus(str, Enum):
    """Lifecycle states for per-channel delivery attempts."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationProvider(str, Enum):
    """Provider identifiers for notification delivery integrations."""

    INTERNAL = "internal"
    SMTP = "smtp"
    SMS_GATEWAY = "sms_gateway"
    PUSH_GATEWAY = "push_gateway"
    WEBHOOK = "webhook"
    EXTERNAL = "external"


class Notification(Base):
    """Notification delivered or deliverable to a user or system actor."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    notification_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    recipient_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    type: Mapped[str] = mapped_column(
        String(length=80),
        nullable=False,
        default=NotificationType.SYSTEM.value,
        index=True,
    )
    channel: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=NotificationChannel.IN_APP.value,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=NotificationPriority.NORMAL.value,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=NotificationStatus.PENDING.value,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )

    entity_type: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    entity_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    request_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dismissed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
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
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )


class NotificationDelivery(Base):
    """Per-channel delivery tracking for a notification."""

    __tablename__ = "notification_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)
    delivery_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )
    notification_id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id"), nullable=False, index=True
    )

    channel: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=NotificationChannel.IN_APP.value,
        index=True,
    )
    provider: Mapped[str | None] = mapped_column(
        String(length=80), nullable=True, index=True
    )
    provider_message_id: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=NotificationDeliveryStatus.PENDING.value,
        index=True,
    )
    attempt_count: Mapped[int] = mapped_column(nullable=False, default=0)

    last_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_response: Mapped[dict[str, Any] | None] = mapped_column(
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


__all__ = [
    "Notification",
    "NotificationChannel",
    "NotificationDelivery",
    "NotificationDeliveryStatus",
    "NotificationPriority",
    "NotificationProvider",
    "NotificationStatus",
    "NotificationType",
]
