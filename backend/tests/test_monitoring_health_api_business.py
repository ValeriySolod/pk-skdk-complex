"""API business behavior checks for Monitoring & Health."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User

BASE_URL = "/api/v1/monitoring_health"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="monitoring-health-business-admin",
            full_name="Monitoring Health Business Admin",
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


@pytest.mark.parametrize(
    ("method", "path", "json"),
    [
        ("GET", "/health", None),
        ("GET", "/health-checks", None),
        ("POST", "/health-checks", {"component": "api"}),
        ("GET", "/metrics", None),
        ("POST", "/metrics", {"metric_name": "cpu", "value": 1}),
        ("GET", "/incidents", None),
        ("POST", "/incidents", {"title": "Outage"}),
        ("PATCH", "/incidents/1", {"status": "investigating"}),
        ("PATCH", "/incidents/1/status", {"status": "resolved"}),
    ],
)
def test_routes_reject_unauthenticated_requests(
    db_session: Session, method: str, path: str, json: dict[str, object] | None
) -> None:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides.pop(get_current_user, None)
    try:
        with TestClient(app) as unauthenticated:
            response = unauthenticated.request(method, f"{BASE_URL}{path}", json=json)
        assert response.status_code == 401
    finally:
        app.dependency_overrides = original_overrides


def test_aggregate_health_uses_real_repositories(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "module": "monitoring_health"}


def test_health_checks_create_filter_paginate_order_and_lookup(client: TestClient) -> None:
    base = datetime(2026, 7, 12, 8, 0, tzinfo=timezone.utc)
    first = client.post(
        f"{BASE_URL}/health-checks",
        json={
            "component": "database",
            "status": "healthy",
            "response_time_ms": 4.25,
            "message": "Primary ready",
            "details": {"replicas": ["db-2"], "ready": True},
            "checked_at": base.isoformat(),
        },
    )
    second = client.post(
        f"{BASE_URL}/health-checks",
        json={
            "component": "api",
            "status": "degraded",
            "message": "Queue delay",
            "checked_at": (base + timedelta(hours=1)).isoformat(),
        },
    )
    assert first.status_code == second.status_code == 201
    first_body, second_body = first.json(), second.json()
    assert first_body["details"] == {"replicas": ["db-2"], "ready": True}
    assert first_body["response_time_ms"] == 4.25
    assert first_body["record_uuid"] and first_body["created_at"]

    listed = client.get(f"{BASE_URL}/health-checks", params={"limit": 1, "offset": 0})
    assert listed.status_code == 200
    assert listed.json()["total"] == 2
    assert listed.json()["items"][0]["id"] == second_body["id"]
    page_two = client.get(f"{BASE_URL}/health-checks", params={"limit": 1, "offset": 1})
    assert page_two.json()["items"][0]["id"] == first_body["id"]

    filtered = client.get(
        f"{BASE_URL}/health-checks",
        params={"component": "database", "status": "healthy", "search": "PRIMARY"},
    )
    assert filtered.json()["total"] == 1
    ranged = client.get(
        f"{BASE_URL}/health-checks",
        params={"checked_from": base.isoformat(), "checked_to": base.isoformat()},
    )
    assert [item["id"] for item in ranged.json()["items"]] == [first_body["id"]]
    assert client.get(f"{BASE_URL}/health-checks/{first_body['id']}").json() == first_body
    assert client.get(
        f"{BASE_URL}/health-checks/uuid/{first_body['record_uuid']}"
    ).json() == first_body


def test_metrics_create_filter_paginate_order_and_lookup(client: TestClient) -> None:
    base = datetime(2026, 7, 12, 9, 0, tzinfo=timezone.utc)
    payloads = [
        {
            "metric_name": "db.connections",
            "category": "database",
            "source": "db-1",
            "value": 7.5,
            "unit": "count",
            "labels": {"pool": "main"},
            "details": ["sample", {"valid": True}],
            "recorded_at": base.isoformat(),
        },
        {
            "metric_name": "http.latency",
            "category": "application",
            "source": "api",
            "value": 25,
            "unit": "ms",
            "recorded_at": (base + timedelta(minutes=1)).isoformat(),
        },
    ]
    created = [client.post(f"{BASE_URL}/metrics", json=payload) for payload in payloads]
    assert all(response.status_code == 201 for response in created)
    first, second = (response.json() for response in created)
    assert first["labels"] == {"pool": "main"}
    assert first["details"] == ["sample", {"valid": True}]

    listed = client.get(f"{BASE_URL}/metrics", params={"limit": 1})
    assert listed.json()["total"] == 2
    assert listed.json()["items"][0]["id"] == second["id"]
    filtered = client.get(
        f"{BASE_URL}/metrics",
        params={
            "category": "database",
            "source": "db-1",
            "unit": "count",
            "search": "CONNECTIONS",
            "recorded_from": base.isoformat(),
            "recorded_to": base.isoformat(),
        },
    )
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["id"] == first["id"]
    assert client.get(f"{BASE_URL}/metrics/{first['id']}").json() == first
    assert client.get(f"{BASE_URL}/metrics/uuid/{first['metric_uuid']}").json() == first


def test_incident_filters_updates_resolution_and_stable_identity(client: TestClient) -> None:
    detected_at = datetime(2026, 7, 12, 10, 0, tzinfo=timezone.utc)
    first_response = client.post(
        f"{BASE_URL}/incidents",
        json={
            "title": "Database latency",
            "severity": "high",
            "source": "apm",
            "component": "database",
            "description": "Queries exceeded threshold",
            "metadata_json": {"trace": "abc", "samples": [1, 2]},
            "detected_at": detected_at.isoformat(),
        },
    )
    second_response = client.post(
        f"{BASE_URL}/incidents",
        json={"title": "Worker retry", "severity": "low", "source": "scheduler"},
    )
    assert first_response.status_code == second_response.status_code == 201
    first, second = first_response.json(), second_response.json()
    assert first["status"] == "open"
    assert first["metadata_json"] == {"trace": "abc", "samples": [1, 2]}

    listed = client.get(f"{BASE_URL}/incidents", params={"limit": 1, "offset": 0})
    assert listed.json()["total"] == 2
    assert listed.json()["items"][0]["id"] == second["id"]
    filtered = client.get(
        f"{BASE_URL}/incidents",
        params={
            "severity": "high",
            "status": "open",
            "source": "apm",
            "component": "database",
            "search": "QUERIES",
            "detected_from": detected_at.isoformat(),
            "detected_to": detected_at.isoformat(),
        },
    )
    assert filtered.json()["total"] == 1

    updated = client.patch(
        f"{BASE_URL}/incidents/{first['id']}",
        json={"severity": "critical", "metadata_json": ["preserved", 2]},
    )
    assert updated.status_code == 200
    assert updated.json()["incident_uuid"] == first["incident_uuid"]
    assert updated.json()["metadata_json"] == ["preserved", 2]
    resolved = client.patch(
        f"{BASE_URL}/incidents/{first['id']}/status",
        json={"status": "resolved", "resolution_summary": "Index restored"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"
    assert resolved.json()["resolved_at"] is not None
    assert resolved.json()["incident_uuid"] == first["incident_uuid"]

    reopened = client.patch(
        f"{BASE_URL}/incidents/{first['id']}", json={"status": "investigating"}
    )
    assert reopened.status_code == 200
    assert reopened.json()["resolved_at"] is None
    by_uuid = client.get(f"{BASE_URL}/incidents/uuid/{first['incident_uuid']}")
    assert by_uuid.json() == client.get(f"{BASE_URL}/incidents/{first['id']}").json()


@pytest.mark.parametrize("resource", ["health-checks", "metrics", "incidents"])
def test_missing_and_invalid_identifiers(client: TestClient, resource: str) -> None:
    assert client.get(f"{BASE_URL}/{resource}/999999").status_code == 404
    assert client.get(f"{BASE_URL}/{resource}/uuid/{uuid4()}").status_code == 404
    invalid_uuid = client.get(f"{BASE_URL}/{resource}/uuid/not-a-uuid")
    assert invalid_uuid.status_code == 422


@pytest.mark.parametrize(
    ("path", "payload", "expected_status"),
    [
        ("health-checks", {"component": "", "status": "healthy"}, 422),
        ("health-checks", {"component": "   ", "status": "healthy"}, 400),
        ("health-checks", {"component": "api", "status": "broken"}, 422),
        ("health-checks", {"component": "api", "response_time_ms": -0.1}, 422),
        ("metrics", {"metric_name": ""}, 422),
        ("metrics", {"metric_name": "   ", "value": 1}, 400),
        ("metrics", {"metric_name": "cpu", "category": "hardware", "value": 1}, 422),
        ("metrics", {"metric_name": "cpu", "value": "not-a-number"}, 422),
        ("incidents", {"title": ""}, 422),
        ("incidents", {"title": "   "}, 400),
        ("incidents", {"title": "Outage", "severity": "urgent"}, 422),
        ("incidents", {"title": "Outage", "status": "finished"}, 422),
        ("incidents", {"title": "Outage", "status": "open", "resolved_at": "2026-07-12T10:00:00Z"}, 400),
    ],
)
def test_create_validation_errors_are_client_errors(
    client: TestClient, path: str, payload: dict[str, object], expected_status: int
) -> None:
    response = client.post(f"{BASE_URL}/{path}", json=payload)
    assert response.status_code == expected_status
    assert response.status_code != 500


@pytest.mark.parametrize(
    ("path", "params", "expected_status"),
    [
        ("health-checks", {"limit": 0}, 422),
        ("health-checks", {"limit": 501}, 422),
        ("metrics", {"offset": -1}, 422),
        ("incidents", {"limit": "many"}, 422),
        ("health-checks", {"checked_from": "bad-date"}, 422),
        ("metrics", {"recorded_from": "2026-07-12T11:00:00Z", "recorded_to": "2026-07-12T10:00:00Z"}, 400),
        ("incidents", {"detected_from": "2026-07-12T11:00:00Z", "detected_to": "2026-07-12T10:00:00Z"}, 400),
        ("incidents", {"resolved_from": "2026-07-12T11:00:00Z", "resolved_to": "2026-07-12T10:00:00Z"}, 400),
        ("incidents", {"created_from": "2026-07-12T11:00:00Z", "created_to": "2026-07-12T10:00:00Z"}, 400),
    ],
)
def test_filter_validation_errors_are_client_errors(
    client: TestClient, path: str, params: dict[str, object], expected_status: int
) -> None:
    response = client.get(f"{BASE_URL}/{path}", params=params)
    assert response.status_code == expected_status
    assert response.status_code != 500


def test_incident_lifecycle_validation_and_naive_datetime_boundary(
    client: TestClient,
) -> None:
    incident = client.post(
        f"{BASE_URL}/incidents",
        json={"title": "Clock boundary", "detected_at": "2026-07-12T10:00:00"},
    ).json()
    before_detection = client.patch(
        f"{BASE_URL}/incidents/{incident['id']}/status",
        json={
            "status": "resolved",
            "resolved_at": "2026-07-12T09:59:59Z",
            "resolution_summary": "Too early",
        },
    )
    assert before_detection.status_code == 400
    assert "resolved_at" in before_detection.json()["detail"]

    blank_summary = client.patch(
        f"{BASE_URL}/incidents/{incident['id']}/status",
        json={"status": "resolved", "resolution_summary": "   "},
    )
    assert blank_summary.status_code == 400
    invalid_status = client.patch(
        f"{BASE_URL}/incidents/{incident['id']}/status", json={"status": "done"}
    )
    assert invalid_status.status_code == 422
    missing = client.patch(
        f"{BASE_URL}/incidents/999999", json={"status": "investigating"}
    )
    assert missing.status_code == 404
