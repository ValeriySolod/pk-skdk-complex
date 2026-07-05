from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.file_storage.models import (
    FileObject,
    FileObjectStatus,
    FileObjectVisibility,
    StorageProvider,
)


BASE_URL = "/api/v1/file-storage"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="file-storage-api-business-admin",
            full_name="File Storage API Business Admin",
            password_hash="not-used",
            role="test",
            is_active=True,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides = original_overrides


def create_test_user(
    db_session: Session,
    username: str = "file-storage-api-business-owner",
) -> User:
    user = User(
        username=username,
        full_name="File Storage API Business Owner",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def file_object_payload(
    *,
    original_filename: str = "controlled-procedure.pdf",
    storage_key: str = "local/documents/controlled-procedure.pdf",
    content_type: str | None = "application/pdf",
    extension: str | None = "pdf",
    size_bytes: int = 2048,
    checksum_sha256: str | None = (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    ),
    storage_provider: str = StorageProvider.LOCAL.value,
    storage_bucket: str | None = "documents",
    storage_path: str = "/var/pk-skdk/documents/controlled-procedure.pdf",
    status: str = FileObjectStatus.AVAILABLE.value,
    access_scope: str = FileObjectVisibility.PRIVATE.value,
    owner_user_id: int | None = None,
    related_entity_type: str | None = "document",
    related_entity_id: str | None = "DOC-API-001",
    metadata_json: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "original_filename": original_filename,
        "storage_key": storage_key,
        "content_type": content_type,
        "extension": extension,
        "size_bytes": size_bytes,
        "checksum_sha256": checksum_sha256,
        "storage_provider": storage_provider,
        "storage_bucket": storage_bucket,
        "storage_path": storage_path,
        "status": status,
        "access_scope": access_scope,
        "owner_user_id": owner_user_id,
        "related_entity_type": related_entity_type,
        "related_entity_id": related_entity_id,
        "metadata_json": metadata_json
        if metadata_json is not None
        else {"source": "api-business-test", "tags": ["file-storage"]},
    }


def create_file_object(
    client: TestClient,
    **payload_overrides: object,
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/objects",
        json=file_object_payload(**payload_overrides),
    )

    assert response.status_code == 201
    return response.json()


def assert_file_object_shape(file_object: dict[str, object]) -> None:
    assert set(file_object) == {
        "id",
        "uuid",
        "original_filename",
        "storage_key",
        "content_type",
        "extension",
        "size_bytes",
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
        "created_at",
        "updated_at",
        "deleted_at",
    }


def assert_list_ids(
    client: TestClient,
    expected_ids: list[int],
    *,
    expected_total: int | None = None,
    **params: object,
) -> None:
    response = client.get(f"{BASE_URL}/objects", params=params)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "limit", "offset"}
    assert [item["id"] for item in body["items"]] == expected_ids
    assert body["total"] == (expected_total if expected_total is not None else len(expected_ids))
    assert body["limit"] == params.get("limit", 100)
    assert body["offset"] == params.get("offset", 0)
    for item in body["items"]:
        assert_file_object_shape(item)


def test_file_object_create_read_list_uuid_lookup_and_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(db_session)
    created = create_file_object(
        client,
        owner_user_id=owner.id,
        access_scope=FileObjectVisibility.INTERNAL.value,
        storage_provider=StorageProvider.S3.value,
        storage_bucket="quality-documents",
        storage_path="quality/controlled-procedure.pdf",
        metadata_json={"document_number": "DOC-API-001", "revision": 1},
    )

    assert_file_object_shape(created)
    assert isinstance(created["id"], int)
    assert isinstance(created["uuid"], str)
    assert created["original_filename"] == "controlled-procedure.pdf"
    assert created["storage_key"] == "local/documents/controlled-procedure.pdf"
    assert created["content_type"] == "application/pdf"
    assert created["extension"] == "pdf"
    assert created["size_bytes"] == 2048
    assert created["storage_provider"] == StorageProvider.S3.value
    assert created["storage_bucket"] == "quality-documents"
    assert created["storage_path"] == "quality/controlled-procedure.pdf"
    assert created["status"] == FileObjectStatus.AVAILABLE.value
    assert created["access_scope"] == FileObjectVisibility.INTERNAL.value
    assert created["owner_user_id"] == owner.id
    assert created["related_entity_type"] == "document"
    assert created["related_entity_id"] == "DOC-API-001"
    assert created["metadata_json"] == {"document_number": "DOC-API-001", "revision": 1}
    assert isinstance(created["created_at"], str)
    assert isinstance(created["updated_at"], str)
    assert created["deleted_at"] is None

    persisted_file = db_session.get(FileObject, created["id"])
    assert persisted_file is not None
    assert str(persisted_file.uuid) == created["uuid"]
    assert persisted_file.metadata_json == {
        "document_number": "DOC-API-001",
        "revision": 1,
    }

    detail_response = client.get(f"{BASE_URL}/objects/{created['id']}")
    uuid_response = client.get(f"{BASE_URL}/objects/uuid/{created['uuid']}")
    list_response = client.get(f"{BASE_URL}/objects")

    assert detail_response.status_code == 200
    assert detail_response.json() == created
    assert uuid_response.status_code == 200
    assert uuid_response.json() == created
    assert list_response.status_code == 200
    assert list_response.json()["items"] == [created]
    assert list_response.json()["total"] == 1
    assert list_response.json()["limit"] == 100
    assert list_response.json()["offset"] == 0


def test_file_object_list_filters_and_pagination(client: TestClient) -> None:
    first_file = create_file_object(
        client,
        original_filename="procedure.pdf",
        storage_key="local/documents/procedure.pdf",
        storage_bucket="documents",
        related_entity_type="document",
        related_entity_id="DOC-API-FILTER-001",
        metadata_json={"kind": "document"},
    )
    second_file = create_file_object(
        client,
        original_filename="avatar.png",
        storage_key="s3/users/avatar.png",
        content_type="image/png",
        extension="png",
        size_bytes=4096,
        checksum_sha256="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        storage_provider=StorageProvider.S3.value,
        storage_bucket="avatars",
        storage_path="users/avatar.png",
        status=FileObjectStatus.PENDING.value,
        access_scope=FileObjectVisibility.PUBLIC.value,
        owner_user_id=42,
        related_entity_type="user",
        related_entity_id="42",
        metadata_json={"kind": "avatar", "dimensions": {"width": 256, "height": 256}},
    )
    third_file = create_file_object(
        client,
        original_filename="import.csv",
        storage_key="external/imports/import.csv",
        content_type="text/csv",
        extension="csv",
        size_bytes=8192,
        checksum_sha256="cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        storage_provider=StorageProvider.EXTERNAL.value,
        storage_bucket="imports",
        storage_path="imports/import.csv",
        status=FileObjectStatus.FAILED.value,
        access_scope=FileObjectVisibility.INTERNAL.value,
        owner_user_id=84,
        related_entity_type="import",
        related_entity_id="IMPORT-API-001",
        metadata_json={"kind": "import", "rows": 12},
    )

    first_id = int(first_file["id"])
    second_id = int(second_file["id"])
    third_id = int(third_file["id"])

    assert_list_ids(client, [third_id, second_id, first_id], expected_total=3)
    assert_list_ids(
        client,
        [third_id, second_id],
        expected_total=3,
        limit=2,
    )
    assert_list_ids(
        client,
        [second_id],
        expected_total=3,
        limit=1,
        offset=1,
    )
    assert_list_ids(client, [second_id], owner_user_id=42)
    assert_list_ids(
        client,
        [third_id],
        access_scope=FileObjectVisibility.INTERNAL.value,
    )
    assert_list_ids(client, [second_id], storage_provider=StorageProvider.S3.value)
    assert_list_ids(client, [first_id], status=FileObjectStatus.AVAILABLE.value)
    assert_list_ids(client, [second_id], content_type="image/png")
    assert_list_ids(client, [first_id], related_entity_type="document")
    assert_list_ids(client, [second_id], related_entity_id="42")
    assert_list_ids(
        client,
        [third_id],
        checksum_sha256="cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    )
    assert_list_ids(client, [first_id], storage_bucket="documents")
    assert_list_ids(client, [], storage_bucket="missing")

    uuid_response = client.get(f"{BASE_URL}/objects/uuid/{second_file['uuid']}")
    id_response = client.get(f"{BASE_URL}/objects/{second_id}")

    assert uuid_response.status_code == 200
    assert id_response.status_code == 200
    assert uuid_response.json() == id_response.json()
    assert uuid_response.json()["metadata_json"] == {
        "kind": "avatar",
        "dimensions": {"width": 256, "height": 256},
    }


def test_file_object_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    missing_get_response = client.get(f"{BASE_URL}/objects/999")
    missing_uuid_response = client.get(f"{BASE_URL}/objects/uuid/{uuid4()}")
    invalid_uuid_response = client.get(f"{BASE_URL}/objects/uuid/not-a-uuid")
    create_validation_response = client.post(
        f"{BASE_URL}/objects",
        json={"original_filename": "missing-required-fields.pdf"},
    )
    negative_size_response = client.post(
        f"{BASE_URL}/objects",
        json=file_object_payload(size_bytes=-1),
    )
    limit_validation_response = client.get(f"{BASE_URL}/objects", params={"limit": 0})
    offset_validation_response = client.get(f"{BASE_URL}/objects", params={"offset": -1})

    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {"detail": "File object not found"}
    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {"detail": "File object not found"}
    assert invalid_uuid_response.status_code == 422
    assert create_validation_response.status_code == 422
    assert negative_size_response.status_code == 422
    assert limit_validation_response.status_code == 422
    assert offset_validation_response.status_code == 422
