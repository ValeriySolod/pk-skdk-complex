"""API contract tests for the Backup & Restore module routes and schemas."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.backup_restore.models import (
    BackupJobStatus,
    BackupJobType,
    RestoreJobStatus,
)
from app.modules.backup_restore.schemas import (
    BackupJobCreate,
    BackupJobListResponse,
    BackupJobRead,
    BackupRestoreHealthRead,
    RestoreJobCreate,
    RestoreJobListResponse,
    RestoreJobRead,
)


BASE_URL = "/api/v1/backup-restore"


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    """Create a TestClient with DB/auth overrides required by the route."""

    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Iterator[Session]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="backup-restore-contract-admin",
            full_name="Backup Restore Contract Admin",
            password_hash="not-used",
            role="test",
            is_active=True,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides = original_overrides


@pytest.fixture()
def unauthenticated_client(db_session: Session) -> Iterator[TestClient]:
    """Create a TestClient with DB override but no auth bypass."""

    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides.pop(get_current_user, None)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides = original_overrides


def _response_json(response: Any) -> dict[str, Any]:
    payload = response.json()
    assert isinstance(payload, dict)
    return payload


def assert_backup_job_contract(job: dict[str, object]) -> None:
    assert set(job) == {
        "id",
        "job_uuid",
        "title",
        "description",
        "backup_type",
        "status",
        "storage_location",
        "storage_path",
        "artifact_name",
        "file_size_bytes",
        "checksum",
        "config",
        "result_summary",
        "metadata_json",
        "error_message",
        "created_by_id",
        "updated_by_id",
        "scheduled_at",
        "started_at",
        "completed_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }


def assert_restore_job_contract(job: dict[str, object]) -> None:
    assert set(job) == {
        "id",
        "job_uuid",
        "backup_job_id",
        "title",
        "status",
        "restore_scope",
        "target_environment",
        "source_artifact_name",
        "source_storage_path",
        "config",
        "result_summary",
        "metadata_json",
        "error_message",
        "created_by_id",
        "updated_by_id",
        "started_at",
        "completed_at",
        "created_at",
        "updated_at",
        "deleted_at",
    }


def create_backup_job(client: TestClient) -> dict[str, Any]:
    response = client.post(
        f"{BASE_URL}/backup-jobs",
        json={
            "title": "Nightly database backup",
            "description": "Contract test backup",
            "backup_type": "full",
            "status": "pending",
            "storage_location": "local",
            "storage_path": "/backups/nightly.dump",
            "artifact_name": "nightly.dump",
            "config": {"include": ["public"]},
            "metadata_json": {"source": "contract-test"},
            "created_by_id": 1,
        },
    )
    assert response.status_code == 201
    return _response_json(response)


def create_restore_job(client: TestClient, backup_job_id: int) -> dict[str, Any]:
    response = client.post(
        f"{BASE_URL}/restore-jobs",
        json={
            "backup_job_id": backup_job_id,
            "title": "Restore staging database",
            "status": "pending",
            "restore_scope": "database",
            "target_environment": "staging",
            "source_artifact_name": "nightly.dump",
            "source_storage_path": "/backups/nightly.dump",
            "config": {"schemas": ["public"]},
            "metadata_json": {"source": "contract-test"},
            "created_by_id": 1,
        },
    )
    assert response.status_code == 201
    return _response_json(response)


def test_backup_restore_health_contract(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    payload = _response_json(response)

    assert payload == {"module": "backup_restore", "status": "ok"}
    schema = BackupRestoreHealthRead.model_validate(payload)
    assert schema.module == "backup_restore"
    assert schema.status == "ok"


def test_backup_restore_routes_require_authenticated_user(
    unauthenticated_client: TestClient,
) -> None:
    get_paths = (
        f"{BASE_URL}/health",
        f"{BASE_URL}/backup-jobs",
        f"{BASE_URL}/backup-jobs/1",
        f"{BASE_URL}/backup-jobs/uuid/00000000-0000-4000-8000-000000000001",
        f"{BASE_URL}/restore-jobs",
        f"{BASE_URL}/restore-jobs/1",
        f"{BASE_URL}/restore-jobs/uuid/00000000-0000-4000-8000-000000000002",
    )

    for path in get_paths:
        response = unauthenticated_client.get(path)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"

    create_response = unauthenticated_client.post(
        f"{BASE_URL}/backup-jobs",
        json={"title": "Unauthenticated backup"},
    )
    assert create_response.status_code == 401
    assert create_response.headers["www-authenticate"] == "Bearer"


def test_backup_restore_routes_are_registered(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = _response_json(response)["paths"]

    assert f"{BASE_URL}/health" in paths
    assert f"{BASE_URL}/backup-jobs" in paths
    assert f"{BASE_URL}/backup-jobs/{{job_id}}" in paths
    assert f"{BASE_URL}/backup-jobs/{{job_id}}/status" in paths
    assert f"{BASE_URL}/backup-jobs/uuid/{{job_uuid}}" in paths
    assert f"{BASE_URL}/restore-jobs" in paths
    assert f"{BASE_URL}/restore-jobs/{{job_id}}" in paths
    assert f"{BASE_URL}/restore-jobs/{{job_id}}/status" in paths
    assert f"{BASE_URL}/restore-jobs/uuid/{{job_uuid}}" in paths

    health_route = paths[f"{BASE_URL}/health"]["get"]
    assert health_route["tags"] == ["Backup & Restore"]
    response_schema = health_route["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert response_schema["$ref"].endswith("/BackupRestoreHealthRead")


def test_backup_job_create_read_list_and_status_contract(client: TestClient) -> None:
    created = create_backup_job(client)
    detail_response = client.get(f"{BASE_URL}/backup-jobs/{created['id']}")
    uuid_response = client.get(f"{BASE_URL}/backup-jobs/uuid/{created['job_uuid']}")
    list_response = client.get(
        f"{BASE_URL}/backup-jobs",
        params={
            "backup_type": "full",
            "status": "pending",
            "storage_location": "local",
            "limit": 25,
            "offset": 0,
        },
    )
    update_response = client.patch(
        f"{BASE_URL}/backup-jobs/{created['id']}/status",
        json={
            "status": "completed",
            "result_summary": {"tables": 12},
            "file_size_bytes": 4096,
            "checksum": "sha256:contract",
            "updated_by_id": 1,
        },
    )

    assert_backup_job_contract(created)
    assert created["backup_type"] == "full"
    assert created["config"] == {"include": ["public"]}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]
    assert uuid_response.status_code == 200
    assert uuid_response.json()["job_uuid"] == created["job_uuid"]

    assert list_response.status_code == 200
    body = _response_json(list_response)
    assert set(body) == {"items", "total", "limit", "offset"}
    assert body["total"] == 1
    assert body["limit"] == 25
    assert len(body["items"]) == 1
    assert_backup_job_contract(body["items"][0])

    assert update_response.status_code == 200
    updated = _response_json(update_response)
    assert updated["status"] == "completed"
    assert updated["result_summary"] == {"tables": 12}
    assert updated["file_size_bytes"] == 4096


def test_restore_job_create_read_list_and_status_contract(client: TestClient) -> None:
    backup_job = create_backup_job(client)
    created = create_restore_job(client, backup_job["id"])
    detail_response = client.get(f"{BASE_URL}/restore-jobs/{created['id']}")
    uuid_response = client.get(f"{BASE_URL}/restore-jobs/uuid/{created['job_uuid']}")
    list_response = client.get(
        f"{BASE_URL}/restore-jobs",
        params={
            "backup_job_id": backup_job["id"],
            "status": "pending",
            "restore_scope": "database",
            "target_environment": "staging",
            "limit": 25,
            "offset": 0,
        },
    )
    update_response = client.patch(
        f"{BASE_URL}/restore-jobs/{created['id']}/status",
        json={
            "status": "running",
            "result_summary": {"phase": "precheck"},
            "updated_by_id": 1,
        },
    )

    assert_restore_job_contract(created)
    assert created["backup_job_id"] == backup_job["id"]
    assert created["config"] == {"schemas": ["public"]}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]
    assert uuid_response.status_code == 200
    assert uuid_response.json()["job_uuid"] == created["job_uuid"]

    assert list_response.status_code == 200
    body = _response_json(list_response)
    assert set(body) == {"items", "total", "limit", "offset"}
    assert body["total"] == 1
    assert body["limit"] == 25
    assert len(body["items"]) == 1
    assert_restore_job_contract(body["items"][0])

    assert update_response.status_code == 200
    updated = _response_json(update_response)
    assert updated["status"] == "running"
    assert updated["result_summary"] == {"phase": "precheck"}


def test_backup_restore_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    missing_backup = client.get(f"{BASE_URL}/backup-jobs/999")
    missing_restore = client.get(f"{BASE_URL}/restore-jobs/999")
    missing_backup_uuid = client.get(
        f"{BASE_URL}/backup-jobs/uuid/00000000-0000-4000-8000-000000000001"
    )
    missing_restore_uuid = client.get(
        f"{BASE_URL}/restore-jobs/uuid/00000000-0000-4000-8000-000000000002"
    )
    invalid_backup_uuid = client.get(f"{BASE_URL}/backup-jobs/uuid/not-a-uuid")
    invalid_restore_uuid = client.get(f"{BASE_URL}/restore-jobs/uuid/not-a-uuid")
    invalid_create = client.post(
        f"{BASE_URL}/backup-jobs",
        json={"backup_type": "full"},
    )
    invalid_query = client.get(f"{BASE_URL}/backup-jobs?limit=0")
    missing_backup_restore = client.post(
        f"{BASE_URL}/restore-jobs",
        json={
            "backup_job_id": 999,
            "title": "Restore missing backup",
            "restore_scope": "database",
        },
    )

    assert missing_backup.status_code == 404
    assert missing_backup.json() == {"detail": "Backup job not found"}
    assert missing_restore.status_code == 404
    assert missing_restore.json() == {"detail": "Restore job not found"}
    assert missing_backup_uuid.status_code == 404
    assert missing_backup_uuid.json() == {"detail": "Backup job not found"}
    assert missing_restore_uuid.status_code == 404
    assert missing_restore_uuid.json() == {"detail": "Restore job not found"}
    assert invalid_backup_uuid.status_code == 422
    assert invalid_restore_uuid.status_code == 422
    assert invalid_create.status_code == 422
    assert invalid_query.status_code == 422
    assert missing_backup_restore.status_code == 404
    assert missing_backup_restore.json() == {"detail": "Backup job not found"}


def test_backup_restore_schemas_validate_and_serialize() -> None:
    created_at = datetime(2026, 7, 8, 10, 0, tzinfo=UTC)

    backup_create = BackupJobCreate.model_validate(
        {
            "title": "Manual backup",
            "backup_type": "manual",
            "status": "pending",
            "config": {"include": ["public"]},
            "metadata_json": {"source": "contract-test"},
        }
    )
    backup_read = BackupJobRead.model_validate(
        {
            **backup_create.model_dump(),
            "id": 1,
            "job_uuid": "00000000-0000-4000-8000-000000000001",
            "description": None,
            "storage_location": None,
            "storage_path": None,
            "artifact_name": None,
            "file_size_bytes": None,
            "checksum": None,
            "result_summary": None,
            "error_message": None,
            "created_by_id": None,
            "updated_by_id": None,
            "scheduled_at": None,
            "started_at": None,
            "completed_at": None,
            "created_at": created_at,
            "updated_at": created_at,
            "deleted_at": None,
        }
    )
    backup_list = BackupJobListResponse(
        items=[backup_read],
        total=1,
        limit=10,
        offset=0,
    )

    assert backup_create.backup_type == BackupJobType.MANUAL
    assert backup_create.status == BackupJobStatus.PENDING
    assert backup_list.model_dump(mode="json")["items"][0]["status"] == "pending"

    restore_create = RestoreJobCreate.model_validate(
        {
            "backup_job_id": 1,
            "title": "Restore database",
            "status": "pending",
            "restore_scope": "database",
            "target_environment": "staging",
        }
    )
    restore_read = RestoreJobRead.model_validate(
        {
            **restore_create.model_dump(),
            "id": 1,
            "job_uuid": "00000000-0000-4000-8000-000000000002",
            "source_artifact_name": None,
            "source_storage_path": None,
            "config": None,
            "result_summary": None,
            "metadata_json": None,
            "error_message": None,
            "created_by_id": None,
            "updated_by_id": None,
            "started_at": None,
            "completed_at": None,
            "created_at": created_at,
            "updated_at": created_at,
            "deleted_at": None,
        }
    )
    restore_list = RestoreJobListResponse(
        items=[restore_read],
        total=1,
        limit=10,
        offset=0,
    )

    assert restore_create.status == RestoreJobStatus.PENDING
    assert restore_list.model_dump(mode="json")["items"][0]["status"] == "pending"
