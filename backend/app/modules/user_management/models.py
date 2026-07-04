from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserManagementProfile(Base):
    """Administrative user profile linked to the core auth user account."""

    __tablename__ = "user_management_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True
    )

    display_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    personnel_number: Mapped[str | None] = mapped_column(
        String(length=80), nullable=True
    )
    job_title: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(length=80), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserManagementRoleAssignment(Base):
    """Role assignment for a user within an optional business scope."""

    __tablename__ = "user_management_role_assignments"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_code",
            "scope_type",
            "scope_id",
            name="uq_user_management_role_assignment_scope",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    role_code: Mapped[str] = mapped_column(String(length=120), nullable=False)
    scope_type: Mapped[str | None] = mapped_column(String(length=80), nullable=True)
    scope_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    assigned_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class UserManagementAuditEvent(Base):
    """Audit trail for administrative user-management actions."""

    __tablename__ = "user_management_audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    target_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    event_type: Mapped[str] = mapped_column(String(length=120), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
