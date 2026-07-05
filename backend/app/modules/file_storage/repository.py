"""Repository skeleton for the file storage module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.file_storage.models import FileObject, FileObjectStatus


class FileStorageRepository:
    """Persistence operations for stored file metadata."""

    _mutable_fields = frozenset(
        {
            "original_filename",
            "content_type",
            "extension",
            "checksum_sha256",
            "storage_provider",
            "storage_bucket",
            "storage_path",
            "status",
            "access_scope",
            "owner_user_id",
            "related_entity_type",
            "related_entity_id",
            "metadata_json",
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, file_object: FileObject) -> FileObject:
        self.db.add(file_object)
        self.db.flush()
        return file_object

    def create_file_object(self, file_object: FileObject) -> FileObject:
        return self.create(file_object)

    def get_by_id(self, file_object_id: int) -> FileObject | None:
        return self.db.get(FileObject, file_object_id)

    def get_by_uuid(self, file_object_uuid: UUID) -> FileObject | None:
        return self.db.scalar(
            select(FileObject).where(FileObject.uuid == file_object_uuid),
        )

    def get_by_storage_key(self, storage_key: str) -> FileObject | None:
        return self.db.scalar(
            select(FileObject).where(FileObject.storage_key == storage_key),
        )

    def list(
        self,
        *,
        owner_user_id: int | None = None,
        access_scope: str | None = None,
        storage_provider: str | None = None,
        status: str | None = None,
        content_type: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
        checksum_sha256: str | None = None,
        storage_bucket: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FileObject]:
        query = self._build_query(
            owner_user_id=owner_user_id,
            access_scope=access_scope,
            storage_provider=storage_provider,
            status=status,
            content_type=content_type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            checksum_sha256=checksum_sha256,
            storage_bucket=storage_bucket,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(FileObject.created_at.desc(), FileObject.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        owner_user_id: int | None = None,
        access_scope: str | None = None,
        storage_provider: str | None = None,
        status: str | None = None,
        content_type: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
        checksum_sha256: str | None = None,
        storage_bucket: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        query = self._build_query(
            owner_user_id=owner_user_id,
            access_scope=access_scope,
            storage_provider=storage_provider,
            status=status,
            content_type=content_type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            checksum_sha256=checksum_sha256,
            storage_bucket=storage_bucket,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        file_object_id: int,
        values: Mapping[str, object],
    ) -> FileObject | None:
        file_object = self.get_by_id(file_object_id)
        if file_object is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported file object update fields: {fields}")

        for field, value in values.items():
            setattr(file_object, field, value)

        self.db.flush()
        return file_object

    def delete(self, file_object_id: int) -> bool:
        file_object = self.get_by_id(file_object_id)
        if file_object is None:
            return False

        file_object.status = FileObjectStatus.DELETED.value
        file_object.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, file_object_id: int) -> bool:
        return self.delete(file_object_id)

    def exists(self, file_object_id: int) -> bool:
        return self.get_by_id(file_object_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        owner_user_id: int | None = None,
        access_scope: str | None = None,
        storage_provider: str | None = None,
        status: str | None = None,
        content_type: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
        checksum_sha256: str | None = None,
        storage_bucket: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> Select[tuple[FileObject]]:
        query = select(FileObject)

        if not include_deleted:
            query = query.where(FileObject.deleted_at.is_(None))
        if owner_user_id is not None:
            query = query.where(FileObject.owner_user_id == owner_user_id)
        if access_scope is not None:
            query = query.where(FileObject.access_scope == access_scope)
        if storage_provider is not None:
            query = query.where(FileObject.storage_provider == storage_provider)
        if status is not None:
            query = query.where(FileObject.status == status)
        if content_type is not None:
            query = query.where(FileObject.content_type == content_type)
        if related_entity_type is not None:
            query = query.where(FileObject.related_entity_type == related_entity_type)
        if related_entity_id is not None:
            query = query.where(FileObject.related_entity_id == related_entity_id)
        if checksum_sha256 is not None:
            query = query.where(FileObject.checksum_sha256 == checksum_sha256)
        if storage_bucket is not None:
            query = query.where(FileObject.storage_bucket == storage_bucket)
        if created_from is not None:
            query = query.where(FileObject.created_at >= created_from)
        if created_to is not None:
            query = query.where(FileObject.created_at <= created_to)

        return query


__all__ = ["FileStorageRepository"]
