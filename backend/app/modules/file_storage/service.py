"""Service layer for the file storage module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from app.modules.file_storage.models import FileObject, StoredFile
from app.modules.file_storage.repository import FileStorageRepository


class FileStorageService:
    """Business boundary for stored file metadata operations."""

    def __init__(self, repository: FileStorageRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        status = "ok" if self.repository.health() else "degraded"
        return {"status": status}

    def create(self, file_object: FileObject) -> FileObject:
        return self.create_file_object(file_object)

    def create_file_object(self, file_object: FileObject) -> FileObject:
        return self.repository.create_file_object(file_object)

    def register_file_object(self, file_object: FileObject) -> FileObject:
        return self.create_file_object(file_object)

    def register_stored_file(self, stored_file: StoredFile) -> StoredFile:
        return self.create_file_object(stored_file)

    def list_file_objects(
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
        return self.repository.list(
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
            limit=limit,
            offset=offset,
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
        return self.list_file_objects(
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
            limit=limit,
            offset=offset,
        )

    def list_stored_files(
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
    ) -> list[StoredFile]:
        return self.list_file_objects(
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
            limit=limit,
            offset=offset,
        )

    def count_file_objects(
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
        return self.repository.count(
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
        return self.count_file_objects(
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

    def count_stored_files(
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
        return self.count_file_objects(
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

    def get_file_object(self, file_object_id: int) -> FileObject | None:
        return self.repository.get_by_id(file_object_id)

    def get_by_id(self, file_object_id: int) -> FileObject | None:
        return self.get_file_object(file_object_id)

    def get_stored_file(self, stored_file_id: int) -> StoredFile | None:
        return self.get_file_object(stored_file_id)

    def get_file_object_by_uuid(self, file_object_uuid: UUID) -> FileObject | None:
        return self.repository.get_by_uuid(file_object_uuid)

    def get_by_uuid(self, file_object_uuid: UUID) -> FileObject | None:
        return self.get_file_object_by_uuid(file_object_uuid)

    def get_stored_file_by_uuid(self, stored_file_uuid: UUID) -> StoredFile | None:
        return self.get_file_object_by_uuid(stored_file_uuid)

    def get_file_object_by_storage_key(self, storage_key: str) -> FileObject | None:
        return self.repository.get_by_storage_key(storage_key)

    def get_by_storage_key(self, storage_key: str) -> FileObject | None:
        return self.get_file_object_by_storage_key(storage_key)

    def get_stored_file_by_storage_key(self, storage_key: str) -> StoredFile | None:
        return self.get_file_object_by_storage_key(storage_key)

    def update_file_object(
        self,
        file_object_id: int,
        values: Mapping[str, object],
    ) -> FileObject | None:
        return self.repository.update(file_object_id, values)

    def update(
        self,
        file_object_id: int,
        values: Mapping[str, object],
    ) -> FileObject | None:
        return self.update_file_object(file_object_id, values)

    def update_stored_file(
        self,
        stored_file_id: int,
        values: Mapping[str, object],
    ) -> StoredFile | None:
        return self.update_file_object(stored_file_id, values)

    def set_file_object_status(
        self,
        file_object_id: int,
        status: str,
    ) -> FileObject | None:
        if not status:
            raise ValueError("File object status is required")

        return self.update_file_object(file_object_id, {"status": status})

    def delete_file_object(self, file_object_id: int) -> bool:
        return self.repository.delete(file_object_id)

    def delete(self, file_object_id: int) -> bool:
        return self.delete_file_object(file_object_id)

    def delete_stored_file(self, stored_file_id: int) -> bool:
        return self.delete_file_object(stored_file_id)

    def mark_deleted(self, file_object_id: int) -> bool:
        return self.repository.mark_deleted(file_object_id)

    def mark_file_object_deleted(self, file_object_id: int) -> bool:
        return self.mark_deleted(file_object_id)

    def file_object_exists(self, file_object_id: int) -> bool:
        return self.repository.exists(file_object_id)

    def stored_file_exists(self, stored_file_id: int) -> bool:
        return self.file_object_exists(stored_file_id)

    def exists(self, file_object_id: int) -> bool:
        return self.file_object_exists(file_object_id)

    def require_file_object(self, file_object_id: int) -> FileObject:
        return self._require_file_object(file_object_id)

    def require_stored_file(self, stored_file_id: int) -> StoredFile:
        return self._require_file_object(stored_file_id)

    def require_file_object_by_uuid(self, file_object_uuid: UUID) -> FileObject:
        file_object = self.repository.get_by_uuid(file_object_uuid)
        if file_object is None:
            raise ValueError("File object not found")
        return file_object

    def require_stored_file_by_uuid(self, stored_file_uuid: UUID) -> StoredFile:
        return self.require_file_object_by_uuid(stored_file_uuid)

    def _require_file_object(self, file_object_id: int) -> FileObject:
        file_object = self.repository.get_by_id(file_object_id)
        if file_object is None:
            raise ValueError("File object not found")
        return file_object


__all__ = ["FileStorageService"]
