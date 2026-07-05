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
from app.modules.document_management.models import (
    Document,
    DocumentCategory,
    DocumentVersion,
)


BASE_URL = "/api/v1/document-management"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="document-api-business-admin",
            full_name="Document API Business Admin",
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


def create_document(
    client: TestClient,
    *,
    title: str = "Controlled Procedure",
    document_number: str | None = "DOC-API-001",
    document_type: str = "procedure",
    status: str = "draft",
    description: str | None = "Created through API business test",
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/documents",
        json={
            "title": title,
            "document_number": document_number,
            "description": description,
            "document_type": document_type,
            "status": status,
            "organization_id": None,
            "owner_user_id": None,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_category(
    client: TestClient,
    *,
    name: str = "Policies",
    code: str = "POLICY",
    description: str | None = "Policy documents",
    is_active: bool = True,
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/categories",
        json={
            "name": name,
            "code": code,
            "description": description,
            "is_active": is_active,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_document_version(
    client: TestClient,
    document_id: int,
    *,
    version: str = "1.0",
    file_name: str = "controlled-procedure-v1.pdf",
    storage_path: str = "/documents/controlled-procedure-v1.pdf",
    checksum: str | None = "checksum-v1",
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/documents/{document_id}/versions",
        json={
            "document_id": document_id,
            "version": version,
            "file_name": file_name,
            "storage_path": storage_path,
            "checksum": checksum,
            "uploaded_by": None,
        },
    )

    assert response.status_code == 201
    return response.json()


def add_document_attachment(
    client: TestClient,
    document_id: int,
    *,
    version: str = "attachment-1",
    file_name: str = "evidence.pdf",
    storage_path: str = "/documents/evidence.pdf",
    checksum: str | None = "attachment-checksum",
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/documents/{document_id}/attachments",
        json={
            "document_id": document_id,
            "version": version,
            "file_name": file_name,
            "storage_path": storage_path,
            "checksum": checksum,
            "uploaded_by": None,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_document_create_read_list_update_status_and_delete_behavior(
    client: TestClient,
    db_session: Session,
) -> None:
    created_document = create_document(client)

    assert isinstance(created_document["id"], int)
    assert created_document["title"] == "Controlled Procedure"
    assert created_document["document_number"] == "DOC-API-001"
    assert created_document["document_type"] == "procedure"
    assert created_document["status"] == "draft"
    assert created_document["organization_id"] is None
    assert created_document["owner_user_id"] is None
    assert isinstance(created_document["created_at"], str)
    assert isinstance(created_document["updated_at"], str)

    persisted_document = db_session.get(Document, created_document["id"])
    assert persisted_document is not None
    assert persisted_document.title == "Controlled Procedure"

    update_response = client.patch(
        f"{BASE_URL}/documents/{created_document['id']}",
        json={
            "title": "Controlled Procedure Updated",
            "status": "review",
            "description": "Updated through API business test",
        },
    )
    detail_response = client.get(f"{BASE_URL}/documents/{created_document['id']}")
    list_response = client.get(f"{BASE_URL}/documents")
    custom_status_response = client.patch(
        f"{BASE_URL}/documents/{created_document['id']}/status/approved",
    )
    archive_response = client.post(
        f"{BASE_URL}/documents/{created_document['id']}/archive",
    )
    activate_response = client.post(
        f"{BASE_URL}/documents/{created_document['id']}/activate",
    )
    delete_response = client.delete(f"{BASE_URL}/documents/{created_document['id']}")
    deleted_detail_response = client.get(f"{BASE_URL}/documents/{created_document['id']}")

    assert update_response.status_code == 200
    updated_document = update_response.json()
    assert updated_document["id"] == created_document["id"]
    assert updated_document["title"] == "Controlled Procedure Updated"
    assert updated_document["status"] == "review"
    assert updated_document["description"] == "Updated through API business test"

    assert detail_response.status_code == 200
    assert detail_response.json() == updated_document
    assert list_response.status_code == 200
    assert list_response.json() == [updated_document]
    assert custom_status_response.status_code == 200
    assert custom_status_response.json()["status"] == "approved"
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert activate_response.status_code == 200
    assert activate_response.json()["status"] == "active"
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}
    assert deleted_detail_response.status_code == 404
    assert deleted_detail_response.json() == {"detail": "Document not found"}


def test_document_endpoints_return_lookup_validation_and_missing_entity_errors(
    client: TestClient,
) -> None:
    missing_uuid_response = client.get(f"{BASE_URL}/documents/uuid/{uuid4()}")
    invalid_uuid_response = client.get(f"{BASE_URL}/documents/uuid/not-a-uuid")
    validation_response = client.post(
        f"{BASE_URL}/documents",
        json={"title": "Missing document type and status"},
    )
    missing_get_response = client.get(f"{BASE_URL}/documents/999")
    missing_update_response = client.patch(
        f"{BASE_URL}/documents/999",
        json={"title": "Missing"},
    )
    missing_delete_response = client.delete(f"{BASE_URL}/documents/999")
    missing_status_response = client.patch(
        f"{BASE_URL}/documents/999/status/archived",
    )
    missing_archive_response = client.post(f"{BASE_URL}/documents/999/archive")
    missing_activate_response = client.post(f"{BASE_URL}/documents/999/activate")

    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {"detail": "Document not found"}
    assert invalid_uuid_response.status_code == 422
    assert validation_response.status_code == 422
    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {"detail": "Document not found"}
    assert missing_update_response.status_code == 404
    assert missing_update_response.json() == {"detail": "Document not found"}
    assert missing_delete_response.status_code == 404
    assert missing_delete_response.json() == {"detail": "Document not found"}
    assert missing_status_response.status_code == 404
    assert missing_status_response.json() == {"detail": "Document not found"}
    assert missing_archive_response.status_code == 404
    assert missing_archive_response.json() == {"detail": "Document not found"}
    assert missing_activate_response.status_code == 404
    assert missing_activate_response.json() == {"detail": "Document not found"}


def test_category_create_read_list_update_delete_and_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    created_category = create_category(client)

    assert isinstance(created_category["id"], int)
    assert created_category["name"] == "Policies"
    assert created_category["code"] == "POLICY"
    assert created_category["description"] == "Policy documents"
    assert created_category["is_active"] is True

    persisted_category = db_session.get(DocumentCategory, created_category["id"])
    assert persisted_category is not None
    assert persisted_category.code == "POLICY"

    update_response = client.patch(
        f"{BASE_URL}/categories/{created_category['id']}",
        json={
            "name": "Operational Policies",
            "description": "Updated policy documents",
            "is_active": False,
        },
    )
    detail_response = client.get(f"{BASE_URL}/categories/{created_category['id']}")
    list_response = client.get(f"{BASE_URL}/categories")
    delete_response = client.delete(f"{BASE_URL}/categories/{created_category['id']}")
    deleted_detail_response = client.get(
        f"{BASE_URL}/categories/{created_category['id']}",
    )

    assert update_response.status_code == 200
    updated_category = update_response.json()
    assert updated_category["id"] == created_category["id"]
    assert updated_category["name"] == "Operational Policies"
    assert updated_category["code"] == "POLICY"
    assert updated_category["description"] == "Updated policy documents"
    assert updated_category["is_active"] is False

    assert detail_response.status_code == 200
    assert detail_response.json() == updated_category
    assert list_response.status_code == 200
    assert list_response.json() == [updated_category]
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}
    assert deleted_detail_response.status_code == 404
    assert deleted_detail_response.json() == {"detail": "Document category not found"}


def test_category_endpoints_return_validation_and_missing_entity_errors(
    client: TestClient,
) -> None:
    validation_response = client.post(
        f"{BASE_URL}/categories",
        json={"name": "Missing Code"},
    )
    missing_get_response = client.get(f"{BASE_URL}/categories/999")
    missing_update_response = client.patch(
        f"{BASE_URL}/categories/999",
        json={"name": "Missing"},
    )
    missing_delete_response = client.delete(f"{BASE_URL}/categories/999")

    assert validation_response.status_code == 422
    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {"detail": "Document category not found"}
    assert missing_update_response.status_code == 404
    assert missing_update_response.json() == {"detail": "Document category not found"}
    assert missing_delete_response.status_code == 404
    assert missing_delete_response.json() == {"detail": "Document category not found"}


def test_version_create_list_latest_detail_and_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    document = create_document(client, document_number="DOC-API-VERSION")
    document_id = int(document["id"])
    first_version = create_document_version(client, document_id)
    second_version = create_document_version(
        client,
        document_id,
        version="2.0",
        file_name="controlled-procedure-v2.pdf",
        storage_path="/documents/controlled-procedure-v2.pdf",
        checksum="checksum-v2",
    )

    assert isinstance(first_version["id"], int)
    assert first_version["document_id"] == document_id
    assert first_version["version"] == "1.0"
    assert first_version["file_name"] == "controlled-procedure-v1.pdf"
    assert first_version["storage_path"] == "/documents/controlled-procedure-v1.pdf"
    assert first_version["checksum"] == "checksum-v1"
    assert first_version["uploaded_by"] is None
    assert isinstance(first_version["uploaded_at"], str)

    persisted_version = db_session.get(DocumentVersion, first_version["id"])
    assert persisted_version is not None
    assert persisted_version.document_id == document_id

    list_response = client.get(f"{BASE_URL}/documents/{document_id}/versions")
    latest_response = client.get(f"{BASE_URL}/documents/{document_id}/versions/latest")
    detail_response = client.get(f"{BASE_URL}/versions/{second_version['id']}")

    assert list_response.status_code == 200
    assert list_response.json() == [first_version, second_version]
    assert latest_response.status_code == 200
    assert latest_response.json() == second_version
    assert detail_response.status_code == 200
    assert detail_response.json() == second_version


def test_version_endpoints_return_validation_mismatch_and_missing_entity_errors(
    client: TestClient,
) -> None:
    document = create_document(client, document_number="DOC-API-VERSION-ERRORS")
    document_without_versions = create_document(
        client,
        document_number="DOC-API-NO-VERSIONS",
    )
    document_id = int(document["id"])

    validation_response = client.post(
        f"{BASE_URL}/documents/{document_id}/versions",
        json={"document_id": document_id, "version": "2.0"},
    )
    mismatch_response = client.post(
        f"{BASE_URL}/documents/{document_id}/versions",
        json={
            "document_id": document_id + 1,
            "version": "2.0",
            "file_name": "mismatch.pdf",
            "storage_path": "/documents/mismatch.pdf",
        },
    )
    missing_create_document_response = client.post(
        f"{BASE_URL}/documents/999/versions",
        json={
            "document_id": 999,
            "version": "1.0",
            "file_name": "missing-document.pdf",
            "storage_path": "/documents/missing-document.pdf",
        },
    )
    missing_list_document_response = client.get(f"{BASE_URL}/documents/999/versions")
    missing_latest_document_response = client.get(
        f"{BASE_URL}/documents/999/versions/latest",
    )
    no_latest_response = client.get(
        f"{BASE_URL}/documents/{document_without_versions['id']}/versions/latest",
    )
    missing_version_response = client.get(f"{BASE_URL}/versions/999")

    assert validation_response.status_code == 422
    assert mismatch_response.status_code == 400
    assert mismatch_response.json() == {"detail": "Document id mismatch"}
    assert missing_create_document_response.status_code == 400
    assert missing_create_document_response.json() == {"detail": "Document not found"}
    assert missing_list_document_response.status_code == 404
    assert missing_list_document_response.json() == {"detail": "Document not found"}
    assert missing_latest_document_response.status_code == 404
    assert missing_latest_document_response.json() == {"detail": "Document not found"}
    assert no_latest_response.status_code == 404
    assert no_latest_response.json() == {"detail": "Document version not found"}
    assert missing_version_response.status_code == 404
    assert missing_version_response.json() == {"detail": "Document version not found"}


def test_attachment_create_list_detail_delete_and_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    document = create_document(client, document_number="DOC-API-ATTACHMENT")
    document_id = int(document["id"])
    attachment = add_document_attachment(client, document_id)

    assert isinstance(attachment["id"], int)
    assert attachment["document_id"] == document_id
    assert attachment["version"] == "attachment-1"
    assert attachment["file_name"] == "evidence.pdf"
    assert attachment["storage_path"] == "/documents/evidence.pdf"
    assert attachment["checksum"] == "attachment-checksum"
    assert attachment["uploaded_by"] is None
    assert isinstance(attachment["uploaded_at"], str)

    persisted_attachment = db_session.get(DocumentVersion, attachment["id"])
    assert persisted_attachment is not None
    assert persisted_attachment.file_name == "evidence.pdf"

    list_response = client.get(f"{BASE_URL}/documents/{document_id}/attachments")
    detail_response = client.get(f"{BASE_URL}/attachments/{attachment['id']}")
    delete_response = client.delete(f"{BASE_URL}/attachments/{attachment['id']}")
    deleted_detail_response = client.get(f"{BASE_URL}/attachments/{attachment['id']}")

    assert list_response.status_code == 200
    assert list_response.json() == [attachment]
    assert detail_response.status_code == 200
    assert detail_response.json() == attachment
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}
    assert deleted_detail_response.status_code == 404
    assert deleted_detail_response.json() == {"detail": "Document attachment not found"}


def test_attachment_endpoints_return_validation_mismatch_and_missing_entity_errors(
    client: TestClient,
) -> None:
    document = create_document(client, document_number="DOC-API-ATTACHMENT-ERRORS")
    document_id = int(document["id"])

    validation_response = client.post(
        f"{BASE_URL}/documents/{document_id}/attachments",
        json={"document_id": document_id, "version": "attachment"},
    )
    mismatch_response = client.post(
        f"{BASE_URL}/documents/{document_id}/attachments",
        json={
            "document_id": document_id + 1,
            "version": "attachment",
            "file_name": "mismatch.pdf",
            "storage_path": "/documents/mismatch.pdf",
        },
    )
    missing_create_document_response = client.post(
        f"{BASE_URL}/documents/999/attachments",
        json={
            "document_id": 999,
            "version": "attachment",
            "file_name": "missing-document.pdf",
            "storage_path": "/documents/missing-document.pdf",
        },
    )
    missing_list_document_response = client.get(f"{BASE_URL}/documents/999/attachments")
    missing_attachment_response = client.get(f"{BASE_URL}/attachments/999")
    missing_delete_response = client.delete(f"{BASE_URL}/attachments/999")

    assert validation_response.status_code == 422
    assert mismatch_response.status_code == 400
    assert mismatch_response.json() == {"detail": "Document id mismatch"}
    assert missing_create_document_response.status_code == 400
    assert missing_create_document_response.json() == {"detail": "Document not found"}
    assert missing_list_document_response.status_code == 404
    assert missing_list_document_response.json() == {"detail": "Document not found"}
    assert missing_attachment_response.status_code == 404
    assert missing_attachment_response.json() == {
        "detail": "Document attachment not found",
    }
    assert missing_delete_response.status_code == 404
    assert missing_delete_response.json() == {
        "detail": "Document attachment not found",
    }
