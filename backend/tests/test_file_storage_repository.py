from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.modules.file_storage.models import (
    FileObject,
    FileObjectStatus,
    FileObjectVisibility,
    StorageProvider,
    StoredFile,
)
from app.modules.file_storage.repository import FileStorageRepository


def create_test_user(
    db_session: Session,
    username: str = "file-storage-repository-user",
) -> User:
    user = User(
        username=username,
        full_name="File Storage Repository User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_file_object(
    repository: FileStorageRepository,
    *,
    original_filename: str = "procedure.pdf",
    storage_key: str = "local/documents/procedure.pdf",
    content_type: str | None = "application/pdf",
    extension: str | None = "pdf",
    size_bytes: int = 1024,
    checksum_sha256: str | None = (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    ),
    storage_provider: str = StorageProvider.LOCAL.value,
    storage_bucket: str | None = "documents",
    storage_path: str = "/var/pk-skdk/documents/procedure.pdf",
    status: str = FileObjectStatus.AVAILABLE.value,
    access_scope: str = FileObjectVisibility.PRIVATE.value,
    owner_user_id: int | None = None,
    related_entity_type: str | None = "document",
    related_entity_id: str | None = "DOC-001",
    metadata_json: dict[str, object] | None = None,
    created_at: datetime | None = None,
) -> FileObject:
    return repository.create(
        FileObject(
            original_filename=original_filename,
            storage_key=storage_key,
            content_type=content_type,
            extension=extension,
            size_bytes=size_bytes,
            checksum_sha256=checksum_sha256,
            storage_provider=storage_provider,
            storage_bucket=storage_bucket,
            storage_path=storage_path,
            status=status,
            access_scope=access_scope,
            owner_user_id=owner_user_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            metadata_json=metadata_json
            if metadata_json is not None
            else {"source": "repository-test", "tags": ["file-storage"]},
            created_at=created_at,
        ),
    )


def test_file_object_create_lookup_aliases_metadata_and_missing_results(
    db_session: Session,
) -> None:
    repository = FileStorageRepository(db_session)
    owner = create_test_user(db_session)

    file_object = create_file_object(repository, owner_user_id=owner.id)
    stored_file: StoredFile = repository.create_file_object(
        StoredFile(
            original_filename="appendix.txt",
            storage_key="local/documents/appendix.txt",
            content_type="text/plain",
            extension="txt",
            size_bytes=128,
            storage_provider=StorageProvider.LOCAL.value,
            storage_bucket="documents",
            storage_path="/var/pk-skdk/documents/appendix.txt",
            status=FileObjectStatus.PENDING.value,
            access_scope=FileObjectVisibility.INTERNAL.value,
            owner_user_id=owner.id,
            related_entity_type="document",
            related_entity_id="DOC-002",
            metadata_json={"source": "stored-file-alias", "revision": 1},
        ),
    )

    assert file_object.id is not None
    assert file_object.uuid is not None
    assert file_object.created_at is not None
    assert file_object.updated_at is not None
    assert stored_file.id is not None
    assert repository.get_by_id(file_object.id) == file_object
    assert repository.get_by_uuid(file_object.uuid) == file_object
    assert repository.get_by_storage_key(file_object.storage_key) == file_object
    assert repository.exists(file_object.id) is True
    assert file_object.metadata_json == {
        "source": "repository-test",
        "tags": ["file-storage"],
    }
    assert stored_file.metadata_json == {"source": "stored-file-alias", "revision": 1}

    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.get_by_storage_key("missing/object.bin") is None
    assert repository.exists(999) is False


def test_file_object_list_filters_count_ordering_and_pagination(
    db_session: Session,
) -> None:
    repository = FileStorageRepository(db_session)
    owner = create_test_user(db_session, "file-storage-filter-owner")
    other_owner = create_test_user(db_session, "file-storage-filter-other")

    first_file = create_file_object(
        repository,
        original_filename="procedure.pdf",
        storage_key="local/documents/procedure.pdf",
        storage_bucket="documents",
        owner_user_id=owner.id,
        related_entity_type="document",
        related_entity_id="DOC-001",
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second_file = create_file_object(
        repository,
        original_filename="avatar.png",
        storage_key="s3/users/avatar.png",
        content_type="image/png",
        extension="png",
        size_bytes=2048,
        checksum_sha256="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        storage_provider=StorageProvider.S3.value,
        storage_bucket="avatars",
        storage_path="users/avatar.png",
        status=FileObjectStatus.PENDING.value,
        access_scope=FileObjectVisibility.PUBLIC.value,
        owner_user_id=owner.id,
        related_entity_type="user",
        related_entity_id=str(owner.id),
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third_file = create_file_object(
        repository,
        original_filename="import.csv",
        storage_key="external/imports/import.csv",
        content_type="text/csv",
        extension="csv",
        size_bytes=4096,
        checksum_sha256="cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        storage_provider=StorageProvider.EXTERNAL.value,
        storage_bucket="imports",
        storage_path="imports/import.csv",
        status=FileObjectStatus.FAILED.value,
        access_scope=FileObjectVisibility.INTERNAL.value,
        owner_user_id=other_owner.id,
        related_entity_type="import",
        related_entity_id="IMPORT-001",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert repository.list() == [third_file, second_file, first_file]
    assert repository.list(limit=2) == [third_file, second_file]
    assert repository.list(offset=1, limit=1) == [second_file]

    assert repository.list(owner_user_id=owner.id) == [second_file, first_file]
    assert repository.list(access_scope=FileObjectVisibility.PUBLIC.value) == [
        second_file
    ]
    assert repository.list(storage_provider=StorageProvider.EXTERNAL.value) == [
        third_file
    ]
    assert repository.list(status=FileObjectStatus.AVAILABLE.value) == [first_file]
    assert repository.list(content_type="image/png") == [second_file]
    assert repository.list(related_entity_type="document") == [first_file]
    assert repository.list(related_entity_id=str(owner.id)) == [second_file]
    assert repository.list(
        checksum_sha256="cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    ) == [third_file]
    assert repository.list(storage_bucket="documents") == [first_file]
    assert repository.list(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        third_file,
        second_file,
    ]
    assert repository.list(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [
        second_file,
        first_file,
    ]
    assert repository.list(storage_bucket="missing") == []

    assert repository.count() == 3
    assert repository.count(owner_user_id=owner.id) == 2
    assert repository.count(storage_provider=StorageProvider.S3.value) == 1
    assert repository.count(status=FileObjectStatus.AVAILABLE.value) == 1
    assert repository.count(content_type="application/octet-stream") == 0
    assert repository.count(
        related_entity_type="document",
        storage_bucket="documents",
    ) == 1


def test_file_object_update_preserves_uuid_and_rejects_unsupported_fields(
    db_session: Session,
) -> None:
    repository = FileStorageRepository(db_session)
    file_object = create_file_object(repository)
    original_uuid = file_object.uuid

    updated_file_object = repository.update(
        file_object.id,
        {
            "original_filename": "procedure-final.pdf",
            "content_type": "application/pdf",
            "extension": "pdf",
            "checksum_sha256": (
                "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            ),
            "storage_provider": StorageProvider.S3.value,
            "storage_bucket": "archive",
            "storage_path": "archive/procedure-final.pdf",
            "status": FileObjectStatus.AVAILABLE.value,
            "access_scope": FileObjectVisibility.INTERNAL.value,
            "owner_user_id": None,
            "related_entity_type": "case",
            "related_entity_id": "CASE-001",
            "metadata_json": {"source": "updated", "version": 2},
        },
    )

    assert updated_file_object is file_object
    assert file_object.uuid == original_uuid
    assert repository.get_by_uuid(original_uuid) == file_object
    assert file_object.original_filename == "procedure-final.pdf"
    assert file_object.storage_key == "local/documents/procedure.pdf"
    assert file_object.storage_provider == StorageProvider.S3.value
    assert file_object.storage_bucket == "archive"
    assert file_object.storage_path == "archive/procedure-final.pdf"
    assert file_object.access_scope == FileObjectVisibility.INTERNAL.value
    assert file_object.related_entity_type == "case"
    assert file_object.related_entity_id == "CASE-001"
    assert file_object.metadata_json == {"source": "updated", "version": 2}

    assert repository.update(999, {"status": FileObjectStatus.FAILED.value}) is None
    with pytest.raises(ValueError, match="Unsupported file object update fields: id"):
        repository.update(file_object.id, {"id": 999})


def test_file_object_soft_delete_lifecycle_and_health(
    db_session: Session,
) -> None:
    repository = FileStorageRepository(db_session)
    active_file = create_file_object(
        repository,
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )
    deleted_file = create_file_object(
        repository,
        original_filename="obsolete.pdf",
        storage_key="local/documents/obsolete.pdf",
        storage_path="/var/pk-skdk/documents/obsolete.pdf",
        created_at=datetime(2026, 7, 5, 12, 0, 0),
    )

    assert repository.health() is True
    assert repository.delete(deleted_file.id) is True
    assert deleted_file.status == FileObjectStatus.DELETED.value
    assert deleted_file.deleted_at is not None
    assert repository.get_by_id(deleted_file.id) == deleted_file
    assert repository.exists(deleted_file.id) is True
    assert repository.list() == [active_file]
    assert repository.count() == 1
    assert repository.list(include_deleted=True) == [deleted_file, active_file]
    assert repository.count(include_deleted=True) == 2
    assert repository.count(
        status=FileObjectStatus.DELETED.value,
        include_deleted=True,
    ) == 1

    assert repository.delete(999) is False
    assert repository.mark_deleted(999) is False
