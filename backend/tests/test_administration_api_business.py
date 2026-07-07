"""API business tests for the Administration module."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User

BASE_URL = "/api/v1/administration"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="administration-api-business-admin",
            full_name="Administration API Business Admin",
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


def reference_payload(code: str, *, catalog: str = "system") -> dict[str, object]:
    return {
        "catalog": catalog,
        "code": code,
        "title": f"Reference {code}",
        "description": "Business test reference",
        "status": "active",
        "metadata_json": {"source": "business-test"},
    }


def maintenance_task_payload(code: str, *, status: str = "queued") -> dict[str, object]:
    return {
        "code": code,
        "title": f"Maintenance {code}",
        "description": "Business test maintenance task",
        "status": status,
        "priority": "normal",
        "metadata_json": {"source": "business-test"},
    }


def action_event_payload(
    action: str, *, target_type: str = "reference"
) -> dict[str, object]:
    return {
        "actor_user_id": None,
        "action": action,
        "target_type": target_type,
        "target_id": "business-target",
        "description": "Business test action event",
        "metadata_json": {"source": "business-test"},
    }


def test_health_route_returns_administration_health(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["module"] == "administration"


def test_reference_routes_persist_list_filter_and_lookup_by_id_and_uuid(
    client: TestClient,
) -> None:
    first = client.post(f"{BASE_URL}/references", json=reference_payload("system-main"))
    second = client.post(
        f"{BASE_URL}/references",
        json=reference_payload("workflow-main", catalog="workflow"),
    )

    assert first.status_code == 201
    assert second.status_code == 201
    first_body = first.json()
    assert first_body["code"] == "system-main"
    assert first_body["uuid"]

    filtered = client.get(f"{BASE_URL}/references", params={"catalog": "system"})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert [item["id"] for item in filtered.json()["items"]] == [first_body["id"]]

    by_id = client.get(f"{BASE_URL}/references/{first_body['id']}")
    by_uuid = client.get(f"{BASE_URL}/references/uuid/{first_body['uuid']}")
    assert by_id.status_code == 200
    assert by_uuid.status_code == 200
    assert by_id.json() == by_uuid.json() == first_body


def test_missing_reference_returns_404(client: TestClient) -> None:
    assert client.get(f"{BASE_URL}/references/999").status_code == 404


def test_maintenance_task_routes_persist_list_filter_and_lookup_by_id_and_uuid(
    client: TestClient,
) -> None:
    first = client.post(
        f"{BASE_URL}/maintenance-tasks",
        json=maintenance_task_payload("reindex", status="queued"),
    )
    second = client.post(
        f"{BASE_URL}/maintenance-tasks",
        json=maintenance_task_payload("cleanup", status="completed"),
    )

    assert first.status_code == 201
    assert second.status_code == 201
    task = first.json()
    assert task["code"] == "reindex"
    assert task["uuid"]

    filtered = client.get(f"{BASE_URL}/maintenance-tasks", params={"status": "queued"})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["uuid"] == task["uuid"]

    by_id = client.get(f"{BASE_URL}/maintenance-tasks/{task['id']}")
    by_uuid = client.get(f"{BASE_URL}/maintenance-tasks/uuid/{task['uuid']}")
    assert by_id.status_code == 200
    assert by_uuid.status_code == 200
    assert by_id.json() == by_uuid.json() == task


def test_missing_maintenance_task_returns_404(client: TestClient) -> None:
    assert client.get(f"{BASE_URL}/maintenance-tasks/999").status_code == 404


def test_action_event_routes_persist_list_filter_and_lookup_by_id_and_uuid(
    client: TestClient,
) -> None:
    first = client.post(
        f"{BASE_URL}/action-events",
        json=action_event_payload("reference.created"),
    )
    second = client.post(
        f"{BASE_URL}/action-events",
        json=action_event_payload("maintenance.started", target_type="maintenance"),
    )

    assert first.status_code == 201
    assert second.status_code == 201
    event = first.json()
    assert event["action"] == "reference.created"
    assert event["uuid"]

    filtered = client.get(
        f"{BASE_URL}/action-events", params={"action": "reference.created"}
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["uuid"] == event["uuid"]

    by_id = client.get(f"{BASE_URL}/action-events/{event['id']}")
    by_uuid = client.get(f"{BASE_URL}/action-events/uuid/{event['uuid']}")
    assert by_id.status_code == 200
    assert by_uuid.status_code == 200
    assert by_id.json() == by_uuid.json() == event


def test_missing_action_event_and_invalid_payload_return_errors(
    client: TestClient,
) -> None:
    assert client.get(f"{BASE_URL}/action-events/999").status_code == 404

    invalid_reference = client.post(
        f"{BASE_URL}/references",
        json={**reference_payload(""), "title": ""},
    )
    invalid_task = client.post(
        f"{BASE_URL}/maintenance-tasks",
        json={**maintenance_task_payload(""), "title": ""},
    )
    invalid_event = client.post(
        f"{BASE_URL}/action-events",
        json={**action_event_payload(""), "target_type": ""},
    )

    assert invalid_reference.status_code == 422
    assert invalid_task.status_code == 422
    assert invalid_event.status_code == 422
