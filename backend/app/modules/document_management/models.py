from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Document(Base):
    """Document metadata and lifecycle state."""

    __tablename__ = "documents"
    __table_args__ = (Index("ix_documents_document_number", "document_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False, index=True)
    document_number: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, unique=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_type: Mapped[str] = mapped_column(
        String(length=120), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(length=80), nullable=False, index=True)

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organization_units.id"), nullable=True, index=True
    )
    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

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


class DocumentVersion(Base):
    """Stored file version for a document."""

    __tablename__ = "document_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"), nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(String(length=80), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    uploaded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )


class DocumentCategory(Base):
    """Document category reference entry."""

    __tablename__ = "document_categories"
    __table_args__ = (Index("ix_document_categories_code", "code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(
        String(length=80), nullable=False, unique=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )


class DocumentTag(Base):
    """Document tag reference entry."""

    __tablename__ = "document_tags"
    __table_args__ = (Index("ix_document_tags_name", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(length=120), nullable=False, unique=True
    )
    color: Mapped[str | None] = mapped_column(String(length=40), nullable=True)


class DocumentTagAssignment(Base):
    """Assignment of a tag to a document."""

    __tablename__ = "document_tag_assignments"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "tag_id",
            name="uq_document_tag_assignment_document_tag",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"), nullable=False, index=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("document_tags.id"), nullable=False, index=True
    )


class DocumentPermission(Base):
    """Document permission granted to a principal."""

    __tablename__ = "document_permissions"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "principal_type",
            "principal_id",
            "permission",
            name="uq_document_permission_principal",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"), nullable=False, index=True
    )
    principal_type: Mapped[str] = mapped_column(
        String(length=80), nullable=False, index=True
    )
    principal_id: Mapped[int] = mapped_column(nullable=False, index=True)
    permission: Mapped[str] = mapped_column(
        String(length=80), nullable=False, index=True
    )


class DocumentAuditEvent(Base):
    """Audit trail for document-management actions."""

    __tablename__ = "document_audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(length=120), nullable=False, index=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
