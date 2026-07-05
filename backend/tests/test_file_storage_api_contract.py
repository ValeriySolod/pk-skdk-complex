from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.file_storage import routes as file_storage_routes


BASE_URL = "/api/v1/file-storage"


class FakeSession:
    def commit(self) -> None:
        pass

    def refresh(self, _: object) -> None:
        pass


class FakeFileStorageService:
    def __init__(self) -> None:
        self.now = datetime(2026, 7, 5, 12, 0, tzinfo=UTC)
        self.objects: dict[int, SimpleNamespace] = {
            1: SimpleNamespace(
                id=1,
                uuid=UUID("11111111-1111-4111-8111-111111111111"),
                original_filename="quality-policy.pdf",
                storage_key="documents/quality-policy.pdf",
                content_type="application/pdf",
                extension=".pdf",
                size_bytes=1024,
                checksum_sha256="a" * 64,
                storage_provider="local",
                storage_bucket=None,
                storage_path="/var/pk-skdk/files/quality-policy.pdf",
                status="available",
                access_scope="internal",
                owner_user_id=1,
                related_entity_type="document",
                related_entity_id="DOC-001",
                metadata_json={"document_number": "DOC-001"},
                created_at=self.now,
                updated_at=self.now,
                deleted_at=None,
            ),
        }
        self.next_object_id = 2
        self.last_list_filters: dict[str, object] | None = None
        self.last_count_filters: dict[str, object] | None = None

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def list_file_objects(self, **filters: object) -> list[SimpleNamespace]:
        self.last_list_filters = filters
        return list(self.objects.values())

    def count_file_objects(self, **filters: object) -> int:
        self.last_count_filters = filters
        return len(self.objects)

    def create_file_object(self, file_object: object) -> SimpleNamespace:
        created_object = SimpleNamespace(
            id=self.next_object_id,
            uuid=uuid4(),
            created_at=self.now,
            updated_at=self.now,
            deleted_at=None,
            original_filename=getattr(file_object, "original_filename"),
            storage_key=getattr(file_object, "storage_key"),
            content_type=getattr(file_object, "content_type"),
            extension=getattr(file_object, "extension"),
            size_bytes=getattr(file_object, "size_bytes"),
            checksum_sha256=getattr(file_object, "checksum_sha256"),
            storage_provider=getattr(file_object, "storage_provider"),
            storage_bucket=getattr(file_object, "storage_bucket"),
            storage_path=getattr(file_object, "storage_path"),
            status=getattr(file_object, "status"),
            access_scope=getattr(file_object, "access_scope"),
            owner_user_id=getattr(file_object, "owner_user_id"),
            related_entity_type=getattr(file_object, "related_entity_type"),
            related_entity_id=getattr(file_object, "related_entity_id"),
            metadata_json=getattr(file_object, "metadata_json"),
        )
        self.objects[created_object.id] = created_object
        self.next_object_id += 1
        return created_object

    def get_file_object(self, file_object_id: int) -> SimpleNamespace | None:
        return self.objects.get(file_object_id)

    def get_file_object_by_uuid(
        self,
        file_object_uuid: UUID,
    ) -> SimpleNamespace | None:
        return next(
            (
                file_object
                for file_object in self.objects.values()
                if file_object.uuid == file_object_uuid
            ),
            None,
        )


@pytest.fixture()
def service() -> FakeFileStorageService:
    return FakeFileStorageService()


@pytest.fixture()
def client(
    monkeypatch: pytest.MonkeyPatch,
    service: FakeFileStorageService,
) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()
    original_get_service = file_storage_routes.get_file_storage_service

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="file-storage-contract-admin",
            full_name="File Storage Contract Admin",
            password_hash="not-used",
            role="test",
            is_active=True,
        )

    def override_get_db() -> Generator[FakeSession, None, None]:
        yield FakeSession()

    def override_get_service() -> FakeFileStorageService:
        return service

    monkeypatch.setattr(
        file_storage_routes,
        "get_file_storage_service",
        lambda db=None: service,
    )
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[original_get_service] = override_get_service

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides = original_overrides


def assert_file_object_contract(file_object: dict[str, object]) -> None:
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


def test_file_storage_routes_are_registered(client: TestClient) -> None:
    route_paths = {getattr(route, "path", "") for route in app.routes}

    assert f"{BASE_URL}/health" in route_paths
    assert f"{BASE_URL}/objects" in route_paths
    assert f"{BASE_URL}/objects/{{object_id}}" in route_paths
    assert f"{BASE_URL}/objects/uuid/{{object_uuid}}" in route_paths


def test_file_storage_openapi_contains_expected_paths(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert f"{BASE_URL}/objects" in paths
    assert "get" in paths[f"{BASE_URL}/objects"]
    assert "post" in paths[f"{BASE_URL}/objects"]
    assert f"{BASE_URL}/objects/{{object_id}}" in paths
    assert f"{BASE_URL}/objects/uuid/{{object_uuid}}" in paths


def test_file_storage_health_contract(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_file_storage_list_exposes_response_and_query_contract(
    client: TestClient,
    service: FakeFileStorageService,
) -> None:
    response = client.get(
        f"{BASE_URL}/objects",
        params={
            "owner_user_id": 1,
            "access_scope": "internal",
            "storage_provider": "local",
            "status": "available",
            "content_type": "application/pdf",
            "related_entity_type": "document",
            "related_entity_id": "DOC-001",
            "checksum_sha256": "a" * 64,
            "storage_bucket": "contracts",
            "created_from": "2026-07-05T00:00:00Z",
            "created_to": "2026-07-06T00:00:00Z",
            "include_deleted": False,
            "limit": 25,
            "offset": 5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "limit", "offset"}
    assert body["total"] == 1
    assert body["limit"] == 25
    assert body["offset"] == 5
    assert len(body["items"]) == 1
    assert_file_object_contract(body["items"][0])
    assert service.last_list_filters is not None
    assert service.last_list_filters["limit"] == 25
    assert service.last_list_filters["offset"] == 5
    assert service.last_list_filters["storage_provider"] == "local"
    assert service.last_count_filters is not None
    assert "limit" not in service.last_count_filters
    assert "offset" not in service.last_count_filters


def test_file_storage_create_and_get_contract(client: TestClient) -> None:
    create_response = client.post(
        f"{BASE_URL}/objects",
        json={
            "original_filename": "procedure.pdf",
            "storage_key": "documents/procedure.pdf",
            "content_type": "application/pdf",
            "extension": ".pdf",
            "size_bytes": 2048,
            "checksum_sha256": None,
            "storage_provider": "local",
            "storage_bucket": None,
            "storage_path": "/var/pk-skdk/files/procedure.pdf",
            "status": "pending",
            "access_scope": "private",
            "owner_user_id": 1,
            "related_entity_type": "document",
            "related_entity_id": "DOC-002",
            "metadata_json": {"document_number": "DOC-002"},
        },
    )
    detail_response = client.get(f"{BASE_URL}/objects/2")

    assert create_response.status_code == 201
    created_object = create_response.json()
    assert_file_object_contract(created_object)
    assert created_object["original_filename"] == "procedure.pdf"
    assert created_object["metadata_json"] == {"document_number": "DOC-002"}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == 2


def test_file_storage_uuid_detail_contract(client: TestClient) -> None:
    response = client.get(
        f"{BASE_URL}/objects/uuid/11111111-1111-4111-8111-111111111111",
    )

    assert response.status_code == 200
    assert response.json()["uuid"] == "11111111-1111-4111-8111-111111111111"


def test_file_storage_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    missing_get_response = client.get(f"{BASE_URL}/objects/999")
    missing_uuid_response = client.get(
        f"{BASE_URL}/objects/uuid/22222222-2222-4222-8222-222222222222",
    )
    create_validation_response = client.post(
        f"{BASE_URL}/objects",
        json={"original_filename": "missing-required-fields.pdf"},
    )
    query_validation_response = client.get(f"{BASE_URL}/objects?limit=0")

    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {"detail": "File object not found"}
    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {"detail": "File object not found"}
    assert create_validation_response.status_code == 422
    assert query_validation_response.status_code == 422
