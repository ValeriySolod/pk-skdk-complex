"""Domain model skeletons for the file storage module."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FileObjectStatus(str, Enum):
    """Lifecycle states for stored file metadata."""

    PENDING = "pending"
    AVAILABLE = "available"
    DELETED = "deleted"
    FAILED = "failed"


class FileObjectVisibility(str, Enum):
    """Access scope for a stored file."""

    PRIVATE = "private"
    INTERNAL = "internal"
    PUBLIC = "public"


class StorageProvider(str, Enum):
    """Storage backends supported by the file storage module."""

    LOCAL = "local"
    S3 = "s3"
    EXTERNAL = "external"


class FileObject(Base):
    """Stored file metadata and lifecycle state."""

    __tablename__ = "file_storage_objects"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        default=uuid4,
    )

    original_filename: Mapped[str] = mapped_column(
        String(length=255), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(
        String(length=1024), nullable=False, unique=True
    )
    content_type: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True
    )
    extension: Mapped[str | None] = mapped_column(String(length=32), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(
        String(length=64), nullable=True, index=True
    )

    storage_provider: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=StorageProvider.LOCAL.value,
    )
    storage_bucket: Mapped[str | None] = mapped_column(
        String(length=255), nullable=True
    )
    storage_path: Mapped[str] = mapped_column(String(length=1024), nullable=False)

    status: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=FileObjectStatus.PENDING.value,
        index=True,
    )
    access_scope: Mapped[str] = mapped_column(
        String(length=40),
        nullable=False,
        default=FileObjectVisibility.PRIVATE.value,
        index=True,
    )

    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    related_entity_type: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
    )
    related_entity_id: Mapped[str | None] = mapped_column(
        String(length=120), nullable=True, index=True
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


StoredFile = FileObject


__all__ = [
    "FileObject",
    "FileObjectStatus",
    "FileObjectVisibility",
    "StorageProvider",
    "StoredFile",
]
