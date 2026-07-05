"""Domain model skeletons for the audit log module."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLogEvent(Base):
    """Append-only audit event for user activity and domain changes."""

    __tablename__ = "audit_log_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    event_type: Mapped[str] = mapped_column(
        String(length=120), nullable=False, index=True
    )
    entity_type: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    entity_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )

    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    actor_username: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True
    )

    action: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(length=40), nullable=False, default="success"
    )

    ip_address: Mapped[str | None] = mapped_column(String(length=64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    request_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )

    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
    )
    before_state: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    after_state: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )


__all__ = ["AuditLogEvent"]
