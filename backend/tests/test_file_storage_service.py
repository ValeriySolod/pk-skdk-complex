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
from app.modules.file_storage.service import FileStorageService


@pytest.fixture()
def service(db_session: Session) -> FileStorageService:
    return FileStorageService(FileStorageRepository(db_session))


def create_test_user(
    db_session: Session,
    username: str = "file-storage-service-user",
) -> User:
    user = User(
        username=username,
        full_name="File Storage Service User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_file_object(
    service: FileStorageService,
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
    related_entity_id: str | None = "DOC-SVC-001",
    metadata_json: dict[str, object] | None = None,
    created_at: datetime | None = None,
) -> FileObject:
    return service.create_file_object(
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
            else {"source": "service-test", "tags": ["file-storage"]},
            created_at=created_at,
        ),
    )


def test_file_storage_service_create_lookup_aliases_metadata_and_missing_behavior(
    service: FileStorageService,
    db_session: Session,
) -> None:
    owner = create_test_user(db_session)

    file_object = create_file_object(service, owner_user_id=owner.id)
    created_alias = service.create(
        FileObject(
            original_filename="contract.docx",
            storage_key="local/documents/contract.docx",
            content_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            extension="docx",
            size_bytes=2048,
            storage_path="/var/pk-skdk/documents/contract.docx",
            owner_user_id=owner.id,
        ),
    )
    stored_file: StoredFile = service.register_stored_file(
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
            related_entity_id="DOC-SVC-002",
            metadata_json={"source": "stored-file-alias", "revision": 1},
        ),
    )

    assert file_object.id is not None
    assert file_object.uuid is not None
    assert created_alias.id is not None
    assert stored_file.id is not None
    assert service.get_file_object(file_object.id) == file_object
    assert service.get_by_id(file_object.id) == file_object
    assert service.get_stored_file(stored_file.id) == stored_file
    assert service.get_file_object_by_uuid(file_object.uuid) == file_object
    assert service.get_by_uuid(file_object.uuid) == file_object
    assert service.get_stored_file_by_uuid(stored_file.uuid) == stored_file
    assert service.get_file_object_by_storage_key(file_object.storage_key) == file_object
    assert service.get_by_storage_key(file_object.storage_key) == file_object
    assert service.get_stored_file_by_storage_key(stored_file.storage_key) == stored_file
    assert service.file_object_exists(file_object.id) is True
    assert service.stored_file_exists(stored_file.id) is True
    assert service.exists(file_object.id) is True
    assert service.require_file_object(file_object.id) == file_object
    assert service.require_stored_file(stored_file.id) == stored_file
    assert service.require_file_object_by_uuid(file_object.uuid) == file_object
    assert service.require_stored_file_by_uuid(stored_file.uuid) == stored_file
    assert file_object.metadata_json == {
        "source": "service-test",
        "tags": ["file-storage"],
    }
    assert stored_file.metadata_json == {"source": "stored-file-alias", "revision": 1}

    assert service.get_file_object(999) is None
    assert service.get_file_object_by_uuid(uuid4()) is None
    assert service.get_file_object_by_storage_key("missing/object.bin") is None
    assert service.file_object_exists(999) is False

    with pytest.raises(ValueError, match="File object not found"):
        service.require_file_object(999)

    with pytest.raises(ValueError, match="File object not found"):
        service.require_file_object_by_uuid(uuid4())


def test_file_storage_service_list_filters_count_ordering_and_pagination(
    service: FileStorageService,
    db_session: Session,
) -> None:
    owner = create_test_user(db_session, "file-storage-service-filter-owner")
    other_owner = create_test_user(db_session, "file-storage-service-filter-other")

    first_file = create_file_object(
        service,
        original_filename="procedure.pdf",
        storage_key="local/documents/procedure.pdf",
        storage_bucket="documents",
        owner_user_id=owner.id,
        related_entity_type="document",
        related_entity_id="DOC-SVC-001",
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second_file = create_file_object(
        service,
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
        service,
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
        related_entity_id="IMPORT-SVC-001",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert service.list_file_objects() == [third_file, second_file, first_file]
    assert service.list() == [third_file, second_file, first_file]
    assert service.list_stored_files(limit=2) == [third_file, second_file]
    assert service.list_file_objects(offset=1, limit=1) == [second_file]

    assert service.list_file_objects(owner_user_id=owner.id) == [
        second_file,
        first_file,
    ]
    assert service.list_file_objects(access_scope=FileObjectVisibility.PUBLIC.value) == [
        second_file
    ]
    assert service.list_file_objects(storage_provider=StorageProvider.EXTERNAL.value) == [
        third_file
    ]
    assert service.list_file_objects(status=FileObjectStatus.AVAILABLE.value) == [
        first_file
    ]
    assert service.list_file_objects(content_type="image/png") == [second_file]
    assert service.list_file_objects(related_entity_type="document") == [first_file]
    assert service.list_file_objects(related_entity_id=str(owner.id)) == [second_file]
    assert service.list_file_objects(
        checksum_sha256="cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    ) == [third_file]
    assert service.list_file_objects(storage_bucket="documents") == [first_file]
    assert service.list_file_objects(
        created_from=datetime(2026, 7, 5, 10, 0, 0),
    ) == [third_file, second_file]
    assert service.list_file_objects(
        created_to=datetime(2026, 7, 5, 10, 0, 0),
    ) == [second_file, first_file]
    assert service.list_file_objects(storage_bucket="missing") == []

    assert service.count_file_objects() == 3
    assert service.count() == 3
    assert service.count_stored_files(owner_user_id=owner.id) == 2
    assert service.count_file_objects(storage_provider=StorageProvider.S3.value) == 1
    assert service.count_file_objects(status=FileObjectStatus.AVAILABLE.value) == 1
    assert service.count_file_objects(content_type="application/octet-stream") == 0
    assert service.count_file_objects(
        related_entity_type="document",
        storage_bucket="documents",
    ) == 1


def test_file_storage_service_update_status_uuid_stability_and_delete_lifecycle(
    service: FileStorageService,
) -> None:
    active_file = create_file_object(
        service,
        storage_key="local/documents/active.pdf",
        storage_path="/var/pk-skdk/documents/active.pdf",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )
    deleted_file = create_file_object(
        service,
        original_filename="obsolete.pdf",
        storage_key="local/documents/obsolete.pdf",
        storage_path="/var/pk-skdk/documents/obsolete.pdf",
        created_at=datetime(2026, 7, 5, 12, 0, 0),
    )
    original_uuid = active_file.uuid

    updated_file = service.update_file_object(
        active_file.id,
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
            "related_entity_id": "CASE-SVC-001",
            "metadata_json": {"source": "updated", "version": 2},
        },
    )

    assert updated_file is active_file
    assert service.update(active_file.id, {"status": FileObjectStatus.PENDING.value})
    assert service.update_stored_file(
        active_file.id,
        {"status": FileObjectStatus.AVAILABLE.value},
    )
    assert active_file.uuid == original_uuid
    assert service.get_file_object_by_uuid(original_uuid) == active_file
    assert active_file.original_filename == "procedure-final.pdf"
    assert active_file.storage_key == "local/documents/active.pdf"
    assert active_file.storage_provider == StorageProvider.S3.value
    assert active_file.storage_bucket == "archive"
    assert active_file.storage_path == "archive/procedure-final.pdf"
    assert active_file.access_scope == FileObjectVisibility.INTERNAL.value
    assert active_file.related_entity_type == "case"
    assert active_file.related_entity_id == "CASE-SVC-001"
    assert active_file.metadata_json == {"source": "updated", "version": 2}

    failed_file = service.set_file_object_status(
        active_file.id,
        FileObjectStatus.FAILED.value,
    )
    assert failed_file is active_file
    assert active_file.status == FileObjectStatus.FAILED.value
    assert service.set_file_object_status(999, FileObjectStatus.AVAILABLE.value) is None
    assert service.update_file_object(999, {"status": FileObjectStatus.FAILED.value}) is None

    with pytest.raises(ValueError, match="File object status is required"):
        service.set_file_object_status(active_file.id, "")

    with pytest.raises(ValueError, match="Unsupported file object update fields: id"):
        service.update_file_object(active_file.id, {"id": 999})

    assert service.delete_file_object(deleted_file.id) is True
    assert deleted_file.status == FileObjectStatus.DELETED.value
    assert deleted_file.deleted_at is not None
    assert service.get_file_object(deleted_file.id) == deleted_file
    assert service.file_object_exists(deleted_file.id) is True
    assert service.list_file_objects() == [active_file]
    assert service.count_file_objects() == 1
    assert service.list_file_objects(include_deleted=True) == [deleted_file, active_file]
    assert service.count_file_objects(include_deleted=True) == 2
    assert service.count_file_objects(
        status=FileObjectStatus.DELETED.value,
        include_deleted=True,
    ) == 1

    assert service.delete(999) is False
    assert service.delete_stored_file(999) is False
    assert service.mark_deleted(999) is False
    assert service.mark_file_object_deleted(999) is False


def test_file_storage_service_health_contract(service: FileStorageService) -> None:
    assert service.health() == {"status": "ok"}
