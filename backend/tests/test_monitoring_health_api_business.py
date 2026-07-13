"""API business behavior checks for Monitoring & Health."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.monitoring_health.models import (
    HealthCheckRecord,
    MonitoringMetric,
    SystemIncident,
)
from app.modules.monitoring_health.service import MonitoringHealthService

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
        ("PATCH", "/health-checks/1", {"status": "healthy"}),
        ("GET", "/metrics", None),
        ("POST", "/metrics", {"metric_name": "cpu", "value": 1}),
        ("PATCH", "/metrics/1", {"value": 2}),
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


@pytest.mark.parametrize("field", ["title", "severity", "status", "detected_at"])
def test_incident_update_rejects_null_for_database_required_fields(
    client: TestClient, field: str
) -> None:
    incident = client.post(
        f"{BASE_URL}/incidents", json={"title": "Required fields"}
    ).json()

    response = client.patch(
        f"{BASE_URL}/incidents/{incident['id']}", json={field: None}
    )

    assert response.status_code == 422
    assert client.get(f"{BASE_URL}/incidents/{incident['id']}").status_code == 200


@pytest.mark.parametrize("field", ["component", "status", "checked_at"])
def test_health_check_update_rejects_null_for_database_required_fields(
    client: TestClient, db_session: Session, field: str
) -> None:
    created = client.post(
        f"{BASE_URL}/health-checks",
        json={
            "component": "database",
            "status": "healthy",
            "checked_at": "2026-07-13T08:00:00Z",
        },
    ).json()

    response = client.patch(
        f"{BASE_URL}/health-checks/{created['id']}", json={field: None}
    )

    assert response.status_code == 422
    assert client.get(f"{BASE_URL}/health-checks/{created['id']}").json() == created
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1


@pytest.mark.parametrize("field", ["metric_name", "category", "value", "recorded_at"])
def test_metric_update_rejects_null_for_database_required_fields(
    client: TestClient, db_session: Session, field: str
) -> None:
    created = client.post(
        f"{BASE_URL}/metrics",
        json={
            "metric_name": "cpu.usage",
            "category": "system",
            "value": 42.5,
            "recorded_at": "2026-07-13T08:00:00Z",
        },
    ).json()

    response = client.patch(
        f"{BASE_URL}/metrics/{created['id']}", json={field: None}
    )

    assert response.status_code == 422
    assert client.get(f"{BASE_URL}/metrics/{created['id']}").json() == created
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1


def test_update_omission_keeps_required_fields(
    client: TestClient,
) -> None:
    health_check = client.post(
        f"{BASE_URL}/health-checks", json={"component": "api"}
    ).json()
    metric = client.post(
        f"{BASE_URL}/metrics", json={"metric_name": "jobs", "value": 1}
    ).json()

    updated_health_check = client.patch(
        f"{BASE_URL}/health-checks/{health_check['id']}", json={"message": "ready"}
    )
    updated_metric = client.patch(
        f"{BASE_URL}/metrics/{metric['id']}", json={"unit": "count"}
    )

    assert updated_health_check.status_code == 200
    assert updated_health_check.json()["component"] == health_check["component"]
    assert updated_health_check.json()["message"] == "ready"
    assert updated_metric.status_code == 200
    assert updated_metric.json()["metric_name"] == metric["metric_name"]
    assert updated_metric.json()["value"] == metric["value"]
    assert updated_metric.json()["unit"] == "count"


@pytest.mark.parametrize(
    ("resource", "payload", "detail"),
    [
        ("health-checks", {"status": "healthy"}, "Health check not found"),
        ("metrics", {"value": 2}, "Metric not found"),
    ],
)
def test_health_check_and_metric_updates_return_not_found(
    client: TestClient, resource: str, payload: dict[str, object], detail: str
) -> None:
    response = client.patch(f"{BASE_URL}/{resource}/999999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": detail}


@pytest.mark.parametrize(
    ("resource", "create_payload", "update_method", "update_payload", "error_detail"),
    [
        (
            "health-checks",
            {"component": "api", "message": "original"},
            "update_health_check",
            {"message": "changed"},
            "invalid health check update",
        ),
        (
            "metrics",
            {"metric_name": "queue.depth", "value": 3, "unit": "items"},
            "update_metric",
            {"unit": "changed"},
            "invalid metric update",
        ),
    ],
)
def test_health_check_and_metric_updates_translate_value_errors_and_rollback(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    resource: str,
    create_payload: dict[str, object],
    update_method: str,
    update_payload: dict[str, object],
    error_detail: str,
) -> None:
    created = client.post(f"{BASE_URL}/{resource}", json=create_payload).json()
    rollback_calls = 0
    original_rollback = Session.rollback

    def track_rollback(session: Session) -> None:
        nonlocal rollback_calls
        rollback_calls += 1
        original_rollback(session)

    def fail_update(*_: object, **__: object) -> None:
        raise ValueError(error_detail)

    monkeypatch.setattr(Session, "rollback", track_rollback)
    monkeypatch.setattr(MonitoringHealthService, update_method, fail_update)

    response = client.patch(
        f"{BASE_URL}/{resource}/{created['id']}", json=update_payload
    )

    assert response.status_code == 400
    assert response.json() == {"detail": error_detail}
    assert rollback_calls == 1
    assert client.get(f"{BASE_URL}/{resource}/{created['id']}").json() == created
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1


@pytest.mark.parametrize(
    (
        "resource",
        "create_payload",
        "update_method",
        "get_method",
        "update_payload",
        "mutated_field",
        "mutated_value",
        "conflict_detail",
    ),
    [
        (
            "health-checks",
            {"component": "api", "message": "original"},
            "update_health_check",
            "get_health_check",
            {"message": "changed"},
            "message",
            "changed",
            "Health check could not be updated",
        ),
        (
            "metrics",
            {"metric_name": "queue.depth", "value": 3, "unit": "items"},
            "update_metric",
            "get_metric",
            {"unit": "changed"},
            "unit",
            "changed",
            "Metric could not be updated",
        ),
    ],
)
def test_health_check_and_metric_updates_roll_back_integrity_errors(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    resource: str,
    create_payload: dict[str, object],
    update_method: str,
    get_method: str,
    update_payload: dict[str, object],
    mutated_field: str,
    mutated_value: object,
    conflict_detail: str,
) -> None:
    created = client.post(f"{BASE_URL}/{resource}", json=create_payload).json()
    rollback_calls = 0
    original_rollback = Session.rollback

    def track_rollback(session: Session) -> None:
        nonlocal rollback_calls
        rollback_calls += 1
        original_rollback(session)

    def fail_update(
        service: MonitoringHealthService, entity_id: int, _: object
    ) -> HealthCheckRecord | MonitoringMetric | None:
        entity = getattr(service, get_method)(entity_id)
        assert entity is not None
        setattr(entity, mutated_field, mutated_value)
        db_session.flush()
        raise IntegrityError("forced update failure", {}, RuntimeError("forced"))

    monkeypatch.setattr(Session, "rollback", track_rollback)
    monkeypatch.setattr(MonitoringHealthService, update_method, fail_update)

    response = client.patch(
        f"{BASE_URL}/{resource}/{created['id']}", json=update_payload
    )

    assert response.status_code == 409
    assert response.json() == {"detail": conflict_detail}
    assert rollback_calls == 1
    assert client.get(f"{BASE_URL}/{resource}/{created['id']}").json() == created
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1


def test_incident_status_update_rolls_back_integrity_error(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    created = client.post(
        f"{BASE_URL}/incidents", json={"title": "Rollback required"}
    ).json()

    def fail_status_update(
        service: MonitoringHealthService, incident_id: int, status: object, **_: object
    ) -> SystemIncident | None:
        incident = service.get_incident(incident_id)
        assert incident is not None
        incident.status = "resolved"
        incident.resolved_at = datetime.now(timezone.utc)
        db_session.flush()
        raise IntegrityError("forced status update failure", {}, RuntimeError("forced"))

    monkeypatch.setattr(MonitoringHealthService, "mark_incident_status", fail_status_update)

    response = client.patch(
        f"{BASE_URL}/incidents/{created['id']}/status", json={"status": "resolved"}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Incident status could not be updated"
    persisted = client.get(f"{BASE_URL}/incidents/{created['id']}")
    assert persisted.status_code == 200
    assert persisted.json()["status"] == "open"
    assert persisted.json()["resolved_at"] is None
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1
