"""API contract tests for the Integrations module routes and schemas."""

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
from app.modules.integrations.models import (
    IntegrationConnectionStatus,
    IntegrationEventStatus,
    IntegrationProviderStatus,
    IntegrationSyncJobStatus,
)
from app.modules.integrations.schemas import (
    IntegrationConnectionCreate,
    IntegrationConnectionListResponse,
    IntegrationConnectionRead,
    IntegrationEventCreate,
    IntegrationEventListResponse,
    IntegrationEventRead,
    IntegrationProviderCreate,
    IntegrationProviderListResponse,
    IntegrationProviderRead,
    IntegrationSyncJobCreate,
    IntegrationSyncJobListResponse,
    IntegrationSyncJobRead,
    IntegrationsHealthRead,
)


BASE_URL = "/api/v1/integrations"


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    """Create a TestClient with DB/auth overrides required by the route."""

    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Iterator[Session]:
        yield db_session

    def override_get_current_user() -> object:
        return object()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides = original_overrides


def _response_json(response: Any) -> dict[str, Any]:
    payload = response.json()
    assert isinstance(payload, dict)
    return payload


def assert_provider_contract(provider: dict[str, object]) -> None:
    assert set(provider) == {
        "id",
        "provider_uuid",
        "code",
        "name",
        "description",
        "provider_type",
        "status",
        "auth_type",
        "base_url",
        "capabilities",
        "default_config",
        "metadata_json",
        "created_at",
        "updated_at",
        "deleted_at",
    }


def assert_connection_contract(connection: dict[str, object]) -> None:
    assert set(connection) == {
        "id",
        "connection_uuid",
        "provider_id",
        "name",
        "description",
        "status",
        "environment",
        "external_account_id",
        "config",
        "credentials_ref",
        "sync_settings",
        "metadata_json",
        "last_sync_at",
        "last_error_at",
        "last_error_message",
        "created_by_id",
        "updated_by_id",
        "deleted_by_id",
        "created_at",
        "updated_at",
        "deleted_at",
    }


def assert_sync_job_contract(job: dict[str, object]) -> None:
    assert set(job) == {
        "id",
        "job_uuid",
        "connection_id",
        "sync_type",
        "direction",
        "status",
        "request_payload",
        "result_summary",
        "records_processed",
        "records_succeeded",
        "records_failed",
        "scheduled_at",
        "started_at",
        "completed_at",
        "failed_at",
        "failure_reason",
        "triggered_by_user_id",
        "correlation_id",
        "metadata_json",
        "created_at",
        "updated_at",
    }


def assert_event_contract(event: dict[str, object]) -> None:
    assert set(event) == {
        "id",
        "event_uuid",
        "connection_id",
        "sync_job_id",
        "event_type",
        "status",
        "source",
        "external_event_id",
        "entity_type",
        "entity_id",
        "payload",
        "headers",
        "processing_result",
        "error_message",
        "received_at",
        "processed_at",
        "correlation_id",
        "metadata_json",
        "created_at",
    }


def create_provider(client: TestClient) -> dict[str, Any]:
    response = client.post(
        f"{BASE_URL}/providers",
        json={
            "code": "email-gateway",
            "name": "Email Gateway",
            "description": "Outbound email provider",
            "provider_type": "email",
            "status": "active",
            "auth_type": "api_key",
            "base_url": "https://integrations.example.test",
            "capabilities": {"send": True},
            "default_config": {"timeout": 30},
            "metadata_json": {"source": "contract-test"},
        },
    )
    assert response.status_code == 201
    return _response_json(response)


def create_connection(client: TestClient, provider_id: int) -> dict[str, Any]:
    response = client.post(
        f"{BASE_URL}/connections",
        json={
            "provider_id": provider_id,
            "name": "Production email",
            "description": "Production tenant connection",
            "status": "active",
            "environment": "production",
            "external_account_id": "acct-001",
            "config": {"region": "eu"},
            "credentials_ref": "secret/email/prod",
            "sync_settings": {"interval": "hourly"},
            "metadata_json": {"tenant": "default"},
        },
    )
    assert response.status_code == 201
    return _response_json(response)


def create_sync_job(client: TestClient, connection_id: int) -> dict[str, Any]:
    response = client.post(
        f"{BASE_URL}/sync-jobs",
        json={
            "connection_id": connection_id,
            "sync_type": "contacts",
            "direction": "outbound",
            "status": "queued",
            "request_payload": {"batch": 1},
            "correlation_id": "corr-sync-001",
            "metadata_json": {"source": "contract-test"},
        },
    )
    assert response.status_code == 201
    return _response_json(response)


def test_integrations_health_contract(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    payload = _response_json(response)

    assert payload == {"module": "integrations", "status": "ok"}
    schema = IntegrationsHealthRead.model_validate(payload)
    assert schema.module == "integrations"
    assert schema.status == "ok"


def test_integrations_routes_are_registered(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = _response_json(response)["paths"]

    assert f"{BASE_URL}/health" in paths
    assert f"{BASE_URL}/providers" in paths
    assert f"{BASE_URL}/providers/{{provider_id}}" in paths
    assert f"{BASE_URL}/providers/uuid/{{provider_uuid}}" in paths
    assert f"{BASE_URL}/connections" in paths
    assert f"{BASE_URL}/connections/{{connection_id}}" in paths
    assert f"{BASE_URL}/connections/uuid/{{connection_uuid}}" in paths
    assert f"{BASE_URL}/sync-jobs" in paths
    assert f"{BASE_URL}/sync-jobs/{{job_id}}" in paths
    assert f"{BASE_URL}/sync-jobs/uuid/{{job_uuid}}" in paths
    assert f"{BASE_URL}/events" in paths
    assert f"{BASE_URL}/events/{{event_id}}" in paths
    assert f"{BASE_URL}/events/uuid/{{event_uuid}}" in paths

    health_route = paths[f"{BASE_URL}/health"]["get"]
    assert health_route["tags"] == ["Integrations"]
    response_schema = health_route["responses"]["200"]["content"]["application/json"][
        "schema"
    ]
    assert response_schema["$ref"].endswith("/IntegrationsHealthRead")


def test_provider_create_read_and_list_contract(client: TestClient) -> None:
    created = create_provider(client)
    detail_response = client.get(f"{BASE_URL}/providers/{created['id']}")
    uuid_response = client.get(f"{BASE_URL}/providers/uuid/{created['provider_uuid']}")
    list_response = client.get(
        f"{BASE_URL}/providers",
        params={
            "provider_type": "email",
            "status": "active",
            "auth_type": "api_key",
            "limit": 25,
            "offset": 0,
        },
    )

    assert_provider_contract(created)
    assert created["code"] == "email-gateway"
    assert created["capabilities"] == {"send": True}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]
    assert uuid_response.status_code == 200
    assert uuid_response.json()["provider_uuid"] == created["provider_uuid"]

    assert list_response.status_code == 200
    body = _response_json(list_response)
    assert set(body) == {"items", "total", "limit", "offset"}
    assert body["total"] == 1
    assert body["limit"] == 25
    assert len(body["items"]) == 1
    assert_provider_contract(body["items"][0])


def test_connection_create_read_and_list_contract(client: TestClient) -> None:
    provider = create_provider(client)
    created = create_connection(client, provider["id"])
    detail_response = client.get(f"{BASE_URL}/connections/{created['id']}")
    uuid_response = client.get(
        f"{BASE_URL}/connections/uuid/{created['connection_uuid']}"
    )
    list_response = client.get(
        f"{BASE_URL}/connections",
        params={
            "provider_id": provider["id"],
            "status": "active",
            "environment": "production",
            "limit": 25,
            "offset": 0,
        },
    )

    assert_connection_contract(created)
    assert created["provider_id"] == provider["id"]
    assert created["config"] == {"region": "eu"}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]
    assert uuid_response.status_code == 200
    assert uuid_response.json()["connection_uuid"] == created["connection_uuid"]

    assert list_response.status_code == 200
    body = _response_json(list_response)
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert_connection_contract(body["items"][0])


def test_sync_job_create_read_and_list_contract(client: TestClient) -> None:
    provider = create_provider(client)
    connection = create_connection(client, provider["id"])
    created = create_sync_job(client, connection["id"])
    detail_response = client.get(f"{BASE_URL}/sync-jobs/{created['id']}")
    uuid_response = client.get(f"{BASE_URL}/sync-jobs/uuid/{created['job_uuid']}")
    list_response = client.get(
        f"{BASE_URL}/sync-jobs",
        params={
            "connection_id": connection["id"],
            "sync_type": "contacts",
            "status": "queued",
            "correlation_id": "corr-sync-001",
            "limit": 25,
            "offset": 0,
        },
    )

    assert_sync_job_contract(created)
    assert created["request_payload"] == {"batch": 1}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]
    assert uuid_response.status_code == 200
    assert uuid_response.json()["job_uuid"] == created["job_uuid"]

    assert list_response.status_code == 200
    body = _response_json(list_response)
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert_sync_job_contract(body["items"][0])


def test_event_create_read_and_list_contract(client: TestClient) -> None:
    provider = create_provider(client)
    connection = create_connection(client, provider["id"])
    job = create_sync_job(client, connection["id"])
    create_response = client.post(
        f"{BASE_URL}/events",
        json={
            "connection_id": connection["id"],
            "sync_job_id": job["id"],
            "event_type": "delivery.created",
            "status": "received",
            "source": "webhook",
            "external_event_id": "evt-001",
            "entity_type": "message",
            "entity_id": "msg-001",
            "payload": {"delivered": False},
            "headers": {"x-request-id": "req-001"},
            "correlation_id": "corr-sync-001",
            "metadata_json": {"source": "contract-test"},
        },
    )

    assert create_response.status_code == 201
    created = _response_json(create_response)
    detail_response = client.get(f"{BASE_URL}/events/{created['id']}")
    uuid_response = client.get(f"{BASE_URL}/events/uuid/{created['event_uuid']}")
    list_response = client.get(
        f"{BASE_URL}/events",
        params={
            "connection_id": connection["id"],
            "sync_job_id": job["id"],
            "event_type": "delivery.created",
            "status": "received",
            "source": "webhook",
            "correlation_id": "corr-sync-001",
            "limit": 25,
            "offset": 0,
        },
    )

    assert_event_contract(created)
    assert created["payload"] == {"delivered": False}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]
    assert uuid_response.status_code == 200
    assert uuid_response.json()["event_uuid"] == created["event_uuid"]

    assert list_response.status_code == 200
    body = _response_json(list_response)
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert_event_contract(body["items"][0])


def test_integrations_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    missing_provider = client.get(f"{BASE_URL}/providers/999")
    missing_connection = client.get(f"{BASE_URL}/connections/999")
    missing_job = client.get(f"{BASE_URL}/sync-jobs/999")
    missing_event = client.get(f"{BASE_URL}/events/999")
    create_validation_response = client.post(
        f"{BASE_URL}/providers",
        json={"name": "Missing required code and provider type"},
    )
    query_validation_response = client.get(f"{BASE_URL}/providers?limit=0")

    assert missing_provider.status_code == 404
    assert missing_provider.json() == {"detail": "Integration provider not found"}
    assert missing_connection.status_code == 404
    assert missing_connection.json() == {"detail": "Integration connection not found"}
    assert missing_job.status_code == 404
    assert missing_job.json() == {"detail": "Integration sync job not found"}
    assert missing_event.status_code == 404
    assert missing_event.json() == {"detail": "Integration event not found"}
    assert create_validation_response.status_code == 422
    assert query_validation_response.status_code == 422


def test_integrations_schemas_validate_and_serialize() -> None:
    created_at = datetime(2026, 7, 8, 10, 0, tzinfo=UTC)
    provider_create = IntegrationProviderCreate.model_validate(
        {
            "code": "crm-api",
            "name": "CRM API",
            "provider_type": "crm",
            "status": "active",
            "auth_type": "oauth2",
            "capabilities": {"contacts": True},
            "default_config": {"timeout": 30},
            "metadata_json": {"source": "contract-test"},
        }
    )
    provider_read = IntegrationProviderRead.model_validate(
        {
            **provider_create.model_dump(),
            "id": 1,
            "provider_uuid": "00000000-0000-4000-8000-000000000001",
            "description": None,
            "base_url": None,
            "created_at": created_at,
            "updated_at": created_at,
            "deleted_at": None,
        }
    )
    provider_list = IntegrationProviderListResponse(
        items=[provider_read],
        total=1,
        limit=10,
        offset=0,
    )

    assert provider_create.status == IntegrationProviderStatus.ACTIVE
    assert provider_list.model_dump(mode="json")["items"][0]["status"] == "active"

    connection_create = IntegrationConnectionCreate.model_validate(
        {
            "provider_id": 1,
            "name": "Production CRM",
            "status": "active",
            "environment": "production",
        }
    )
    connection_read = IntegrationConnectionRead.model_validate(
        {
            **connection_create.model_dump(),
            "id": 1,
            "connection_uuid": "00000000-0000-4000-8000-000000000002",
            "description": None,
            "external_account_id": None,
            "config": None,
            "credentials_ref": None,
            "sync_settings": None,
            "metadata_json": None,
            "last_sync_at": None,
            "last_error_at": None,
            "last_error_message": None,
            "created_by_id": None,
            "updated_by_id": None,
            "deleted_by_id": None,
            "created_at": created_at,
            "updated_at": created_at,
            "deleted_at": None,
        }
    )
    connection_list = IntegrationConnectionListResponse(
        items=[connection_read],
        total=1,
        limit=10,
        offset=0,
    )

    assert connection_create.status == IntegrationConnectionStatus.ACTIVE
    assert connection_list.total == 1

    job_create = IntegrationSyncJobCreate.model_validate(
        {
            "connection_id": 1,
            "sync_type": "contacts",
            "status": "queued",
            "request_payload": {"batch": 1},
        }
    )
    job_read = IntegrationSyncJobRead.model_validate(
        {
            **job_create.model_dump(),
            "id": 1,
            "job_uuid": "00000000-0000-4000-8000-000000000003",
            "direction": None,
            "result_summary": None,
            "scheduled_at": None,
            "started_at": None,
            "completed_at": None,
            "failed_at": None,
            "failure_reason": None,
            "triggered_by_user_id": None,
            "correlation_id": None,
            "metadata_json": None,
            "created_at": created_at,
            "updated_at": created_at,
        }
    )
    job_list = IntegrationSyncJobListResponse(
        items=[job_read],
        total=1,
        limit=10,
        offset=0,
    )

    assert job_create.status == IntegrationSyncJobStatus.QUEUED
    assert job_list.items[0].records_processed == 0

    event_create = IntegrationEventCreate.model_validate(
        {
            "connection_id": 1,
            "sync_job_id": 1,
            "event_type": "delivery.created",
            "status": "received",
            "payload": {"ok": True},
        }
    )
    event_read = IntegrationEventRead.model_validate(
        {
            **event_create.model_dump(),
            "id": 1,
            "event_uuid": "00000000-0000-4000-8000-000000000004",
            "source": None,
            "external_event_id": None,
            "entity_type": None,
            "entity_id": None,
            "headers": None,
            "processing_result": None,
            "error_message": None,
            "received_at": created_at,
            "processed_at": None,
            "correlation_id": None,
            "metadata_json": None,
            "created_at": created_at,
        }
    )
    event_list = IntegrationEventListResponse(
        items=[event_read],
        total=1,
        limit=10,
        offset=0,
    )

    assert event_create.status == IntegrationEventStatus.RECEIVED
    assert event_list.model_dump(mode="json")["items"][0]["status"] == "received"
