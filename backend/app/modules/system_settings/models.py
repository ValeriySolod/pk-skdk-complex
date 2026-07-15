"""Domain models for the System Settings module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


json_type = JSONB().with_variant(JSON(), "sqlite")


class SystemSettingStatus(str, Enum):
    """Lifecycle states for persisted system settings."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class SystemSettingValueType(str, Enum):
    """Supported value type indicators for dynamic setting values."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    ARRAY = "array"
    OBJECT = "object"


class SystemSettingDefaultStatus(str, Enum):
    """Lifecycle states for default setting definitions."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class SystemSettingChangeAction(str, Enum):
    """Event types for system setting change history."""

    CREATED = "created"
    UPDATED = "updated"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"
    RESTORED = "restored"
    DEFAULT_APPLIED = "default_applied"


class SystemSetting(Base):
    """Persistent configurable application setting."""

    __tablename__ = "system_settings"
    __table_args__ = (
        UniqueConstraint("category", "key", name="uq_system_settings_category_key"),
        Index("ix_system_settings_category_key", "category", "key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    category: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(length=160), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    value: Mapped[dict[str, Any] | list[Any] | str | int | float | bool | None] = mapped_column(
        json_type,
        nullable=True,
    )
    default_value: Mapped[
        dict[str, Any] | list[Any] | str | int | float | bool | None
    ] = mapped_column(json_type, nullable=True)
    value_type: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=SystemSettingValueType.STRING.value,
        index=True,
    )
    validation_rules: Mapped[dict[str, Any] | None] = mapped_column(
        json_type,
        nullable=True,
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=SystemSettingStatus.DRAFT.value,
        index=True,
    )

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
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )


class SystemSettingDefault(Base):
    """Default value definition for a system setting."""

    __tablename__ = "system_setting_defaults"
    __table_args__ = (
        UniqueConstraint("category", "key", name="uq_system_setting_defaults_category_key"),
        Index("ix_system_setting_defaults_category_key", "category", "key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False, unique=True, index=True, default=uuid4
    )

    category: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(length=160), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_value: Mapped[
        dict[str, Any] | list[Any] | str | int | float | bool | None
    ] = mapped_column(json_type, nullable=True)
    value_type: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=SystemSettingValueType.STRING.value,
        index=True,
    )
    validation_rules: Mapped[dict[str, Any] | None] = mapped_column(
        json_type,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=SystemSettingDefaultStatus.ACTIVE.value,
        index=True,
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class SystemSettingChangeEvent(Base):
    """Append-only audit event describing a system setting change."""

    __tablename__ = "system_setting_change_events"
    __table_args__ = (Index("ix_system_setting_events_category_key", "category", "key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False, unique=True, index=True, default=uuid4
    )
    system_setting_id: Mapped[int | None] = mapped_column(
        ForeignKey("system_settings.id"), nullable=True, index=True
    )

    category: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(length=160), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(length=80), nullable=False, index=True)

    old_value: Mapped[dict[str, Any] | list[Any] | str | int | float | bool | None] = mapped_column(
        json_type,
        nullable=True,
    )
    new_value: Mapped[dict[str, Any] | list[Any] | str | int | float | bool | None] = mapped_column(
        json_type,
        nullable=True,
    )
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(length=120), nullable=True, index=True)
    request_id: Mapped[str | None] = mapped_column(String(length=120), nullable=True, index=True)
    correlation_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        json_type,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )


SystemSettingAuditEvent = SystemSettingChangeEvent


__all__ = [
    "SystemSetting",
    "SystemSettingAuditEvent",
    "SystemSettingChangeAction",
    "SystemSettingChangeEvent",
    "SystemSettingDefault",
    "SystemSettingDefaultStatus",
    "SystemSettingStatus",
    "SystemSettingValueType",
]
