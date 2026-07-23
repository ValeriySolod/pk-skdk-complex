from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.document_management import routes as document_routes
from app.modules.document_management.schemas import DocumentCreate, DocumentUpdate


BASE_URL = "/api/v1/document-management"


class FakeSession:
    def commit(self) -> None:
        pass

    def refresh(self, _: object) -> None:
        pass


class FakeDocumentManagementService:
    def __init__(self) -> None:
        now = datetime(2026, 7, 5, 12, 0, tzinfo=UTC)
        self.documents: dict[int, SimpleNamespace] = {
            1: SimpleNamespace(
                id=1,
                title="Quality Policy",
                document_number="DOC-001",
                description="Approved quality policy",
                document_type="policy",
                status="active",
                organization_id=None,
                owner_user_id=1,
                created_at=now,
                updated_at=now,
            ),
        }
        self.versions: dict[int, SimpleNamespace] = {
            1: SimpleNamespace(
                id=1,
                document_id=1,
                version="1.0",
                file_name="quality-policy.pdf",
                storage_path="/documents/quality-policy.pdf",
                checksum="sha256:contract",
                uploaded_by=1,
                uploaded_at=now,
            ),
        }
        self.categories: dict[int, SimpleNamespace] = {
            1: SimpleNamespace(
                id=1,
                name="Policies",
                code="POLICY",
                description="Policy documents",
                is_active=True,
            ),
        }
        self.next_document_id = 2
        self.next_version_id = 2
        self.next_category_id = 2
        self.now = now

    def list_documents(self) -> list[SimpleNamespace]:
        return list(self.documents.values())

    def create_document(self, payload: DocumentCreate) -> SimpleNamespace:
        document = SimpleNamespace(
            id=self.next_document_id,
            created_at=self.now,
            updated_at=self.now,
            **payload.model_dump(),
        )
        self.documents[document.id] = document
        self.next_document_id += 1
        return document

    def get_document(self, document_id: int) -> SimpleNamespace | None:
        return self.documents.get(document_id)

    def update_document(
        self,
        document_id: int,
        payload: DocumentUpdate,
    ) -> SimpleNamespace | None:
        document = self.documents.get(document_id)
        if document is None:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(document, key, value)
        document.updated_at = self.now
        return document

    def delete_document(self, document_id: int) -> bool:
        return self.documents.pop(document_id, None) is not None

    def list_document_versions(self, document_id: int) -> list[SimpleNamespace]:
        self._require_document(document_id)
        return [
            version
            for version in self.versions.values()
            if version.document_id == document_id
        ]

    def get_latest_document_version(
        self,
        document_id: int,
    ) -> SimpleNamespace | None:
        versions = self.list_document_versions(document_id)
        return versions[-1] if versions else None

    def get_document_version(
        self,
        document_version_id: int,
    ) -> SimpleNamespace | None:
        return self.versions.get(document_version_id)

    def create_version(self, document_version: Any) -> SimpleNamespace:
        self._require_document(document_version.document_id)
        version = self._version_from_payload(document_version)
        self.versions[version.id] = version
        return version

    def list_document_categories(self) -> list[SimpleNamespace]:
        return list(self.categories.values())

    def get_document_category(self, category_id: int) -> SimpleNamespace | None:
        return self.categories.get(category_id)

    def create_document_category(self, category: Any) -> SimpleNamespace:
        created_category = SimpleNamespace(
            id=self.next_category_id,
            name=category.name,
            code=category.code,
            description=category.description,
            is_active=category.is_active,
        )
        self.categories[created_category.id] = created_category
        self.next_category_id += 1
        return created_category

    def update_document_category(
        self,
        category_id: int,
        values: dict[str, object],
    ) -> SimpleNamespace | None:
        category = self.categories.get(category_id)
        if category is None:
            return None
        for key, value in values.items():
            setattr(category, key, value)
        return category

    def delete_document_category(self, category_id: int) -> bool:
        return self.categories.pop(category_id, None) is not None

    def list_document_attachments(self, document_id: int) -> list[SimpleNamespace]:
        return self.list_document_versions(document_id)

    def get_document_attachment(
        self,
        document_version_id: int,
    ) -> SimpleNamespace | None:
        return self.versions.get(document_version_id)

    def add_document_attachment(self, document_version: Any) -> SimpleNamespace:
        self._require_document(document_version.document_id)
        attachment = self._version_from_payload(document_version)
        self.versions[attachment.id] = attachment
        return attachment

    def remove_document_attachment(self, document_version_id: int) -> bool:
        return self.versions.pop(document_version_id, None) is not None

    def _require_document(self, document_id: int) -> SimpleNamespace:
        document = self.documents.get(document_id)
        if document is None:
            raise ValueError("Document not found")
        return document

    def _version_from_payload(self, payload: Any) -> SimpleNamespace:
        version = SimpleNamespace(
            id=self.next_version_id,
            document_id=payload.document_id,
            version=payload.version,
            file_name=payload.file_name,
            storage_path=payload.storage_path,
            checksum=payload.checksum,
            uploaded_by=payload.uploaded_by,
            uploaded_at=self.now,
        )
        self.next_version_id += 1
        return version


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()
    original_get_service = document_routes.get_document_management_service
    service = FakeDocumentManagementService()

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="document-contract-admin",
            full_name="Document Contract Admin",
            password_hash="not-used",
            role="test",
            is_active=True,
        )

    def override_get_db() -> Generator[FakeSession, None, None]:
        yield FakeSession()

    def override_get_service() -> FakeDocumentManagementService:
        return service

    monkeypatch.setattr(
        document_routes,
        "get_document_management_service",
        lambda db=None: service,
    )
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[original_get_service] = override_get_service

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides = original_overrides


def assert_document_contract(document: dict[str, object]) -> None:
    assert set(document) == {
        "id",
        "title",
        "document_number",
        "description",
        "document_type",
        "status",
        "organization_id",
        "owner_user_id",
        "created_at",
        "updated_at",
    }


def assert_version_contract(version: dict[str, object]) -> None:
    assert set(version) == {
        "id",
        "document_id",
        "version",
        "file_name",
        "storage_path",
        "checksum",
        "uploaded_by",
        "uploaded_at",
    }


def assert_category_contract(category: dict[str, object]) -> None:
    assert set(category) == {
        "id",
        "name",
        "code",
        "description",
        "is_active",
    }


def test_document_create_list_get_update_delete_contract(
    client: TestClient,
) -> None:
    create_response = client.post(
        f"{BASE_URL}/documents",
        json={
            "title": "Procedure",
            "document_number": "DOC-002",
            "description": "Controlled procedure",
            "document_type": "procedure",
            "status": "draft",
            "organization_id": None,
            "owner_user_id": 1,
        },
    )
    list_response = client.get(f"{BASE_URL}/documents")
    detail_response = client.get(f"{BASE_URL}/documents/2")
    update_response = client.patch(
        f"{BASE_URL}/documents/2",
        json={"title": "Approved Procedure", "status": "active"},
    )
    delete_response = client.delete(f"{BASE_URL}/documents/2")

    assert create_response.status_code == 201
    created_document = create_response.json()
    assert_document_contract(created_document)
    assert created_document["title"] == "Procedure"
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == 2
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Approved Procedure"
    assert update_response.json()["status"] == "active"
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}


def test_documents_list_requires_authentication() -> None:
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides.pop(get_current_user, None)
    try:
        response = TestClient(app).get(f"{BASE_URL}/documents")
    finally:
        app.dependency_overrides = original_overrides

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_document_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    validation_response = client.post(
        f"{BASE_URL}/documents",
        json={"title": "Missing required fields"},
    )
    missing_get_response = client.get(f"{BASE_URL}/documents/999")
    missing_update_response = client.patch(
        f"{BASE_URL}/documents/999",
        json={"title": "Missing"},
    )
    missing_delete_response = client.delete(f"{BASE_URL}/documents/999")

    assert validation_response.status_code == 422
    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {"detail": "Document not found"}
    assert missing_update_response.status_code == 404
    assert missing_update_response.json() == {"detail": "Document not found"}
    assert missing_delete_response.status_code == 404
    assert missing_delete_response.json() == {"detail": "Document not found"}


def test_category_endpoints_expose_response_contracts(client: TestClient) -> None:
    create_response = client.post(
        f"{BASE_URL}/categories",
        json={
            "name": "Instructions",
            "code": "INSTRUCTION",
            "description": "Work instructions",
            "is_active": True,
        },
    )
    list_response = client.get(f"{BASE_URL}/categories")
    detail_response = client.get(f"{BASE_URL}/categories/2")
    update_response = client.patch(
        f"{BASE_URL}/categories/2",
        json={"description": "Updated instructions", "is_active": False},
    )

    assert create_response.status_code == 201
    assert_category_contract(create_response.json())
    assert list_response.status_code == 200
    assert all(set(item) == set(create_response.json()) for item in list_response.json())
    assert detail_response.status_code == 200
    assert detail_response.json()["code"] == "INSTRUCTION"
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated instructions"
    assert update_response.json()["is_active"] is False


def test_category_endpoints_return_not_found_and_validation_errors(
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
    assert missing_update_response.json() == {
        "detail": "Document category not found",
    }
    assert missing_delete_response.status_code == 404
    assert missing_delete_response.json() == {
        "detail": "Document category not found",
    }


def test_version_endpoints_expose_response_contracts(client: TestClient) -> None:
    create_response = client.post(
        f"{BASE_URL}/documents/1/versions",
        json={
            "document_id": 1,
            "version": "2.0",
            "file_name": "quality-policy-v2.pdf",
            "storage_path": "/documents/quality-policy-v2.pdf",
            "checksum": None,
            "uploaded_by": 1,
        },
    )
    list_response = client.get(f"{BASE_URL}/documents/1/versions")
    latest_response = client.get(f"{BASE_URL}/documents/1/versions/latest")
    detail_response = client.get(f"{BASE_URL}/versions/2")

    assert create_response.status_code == 201
    assert_version_contract(create_response.json())
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert latest_response.status_code == 200
    assert latest_response.json()["version"] == "2.0"
    assert detail_response.status_code == 200
    assert detail_response.json()["file_name"] == "quality-policy-v2.pdf"


def test_version_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    validation_response = client.post(
        f"{BASE_URL}/documents/1/versions",
        json={"document_id": 1, "version": "2.0"},
    )
    mismatch_response = client.post(
        f"{BASE_URL}/documents/1/versions",
        json={
            "document_id": 2,
            "version": "2.0",
            "file_name": "mismatch.pdf",
            "storage_path": "/documents/mismatch.pdf",
        },
    )
    missing_document_response = client.get(f"{BASE_URL}/documents/999/versions")
    missing_version_response = client.get(f"{BASE_URL}/versions/999")

    assert validation_response.status_code == 422
    assert mismatch_response.status_code == 400
    assert mismatch_response.json() == {"detail": "Document id mismatch"}
    assert missing_document_response.status_code == 404
    assert missing_document_response.json() == {"detail": "Document not found"}
    assert missing_version_response.status_code == 404
    assert missing_version_response.json() == {
        "detail": "Document version not found",
    }


def test_attachment_endpoints_expose_response_contracts(client: TestClient) -> None:
    create_response = client.post(
        f"{BASE_URL}/documents/1/attachments",
        json={
            "document_id": 1,
            "version": "attachment-1",
            "file_name": "appendix.pdf",
            "storage_path": "/documents/appendix.pdf",
            "checksum": "sha256:attachment",
            "uploaded_by": 1,
        },
    )
    list_response = client.get(f"{BASE_URL}/documents/1/attachments")
    detail_response = client.get(f"{BASE_URL}/attachments/2")
    delete_response = client.delete(f"{BASE_URL}/attachments/2")

    assert create_response.status_code == 201
    assert_version_contract(create_response.json())
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert detail_response.status_code == 200
    assert detail_response.json()["file_name"] == "appendix.pdf"
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}


def test_attachment_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    validation_response = client.post(
        f"{BASE_URL}/documents/1/attachments",
        json={"document_id": 1, "version": "attachment"},
    )
    missing_document_response = client.get(f"{BASE_URL}/documents/999/attachments")
    missing_attachment_response = client.get(f"{BASE_URL}/attachments/999")
    missing_delete_response = client.delete(f"{BASE_URL}/attachments/999")

    assert validation_response.status_code == 422
    assert missing_document_response.status_code == 404
    assert missing_document_response.json() == {"detail": "Document not found"}
    assert missing_attachment_response.status_code == 404
    assert missing_attachment_response.json() == {
        "detail": "Document attachment not found",
    }
    assert missing_delete_response.status_code == 404
    assert missing_delete_response.json() == {
        "detail": "Document attachment not found",
    }
