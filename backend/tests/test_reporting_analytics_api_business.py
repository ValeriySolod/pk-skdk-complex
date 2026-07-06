"""API business tests for the Reporting & Analytics module."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.reporting_analytics.models import (
    AnalyticsSnapshotPeriod,
    AnalyticsSnapshotStatus,
    DashboardStatus,
    ReportDefinitionStatus,
    ReportOutputFormat,
    ReportRunStatus,
)

BASE_URL = "/api/v1/reporting-analytics"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="reporting-analytics-api-business-admin",
            full_name="Reporting Analytics API Business Admin",
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


def dashboard_payload(code: str, *, category: str = "operations") -> dict[str, object]:
    return {
        "code": code,
        "name": f"Dashboard {code}",
        "description": "Operations dashboard",
        "category": category,
        "status": DashboardStatus.ACTIVE.value,
        "owner_user_id": None,
        "layout_config": {"columns": 12},
        "widget_config": {"widgets": [{"type": "metric"}]},
        "filter_config": {"region": "global"},
    }


def report_payload(code: str, *, category: str = "operations") -> dict[str, object]:
    return {
        "code": code,
        "name": f"Report {code}",
        "description": "Operations report",
        "category": category,
        "source_module": "orders",
        "status": ReportDefinitionStatus.ACTIVE.value,
        "default_format": ReportOutputFormat.XLSX.value,
        "owner_user_id": None,
        "query_config": {"source": "orders"},
        "filter_schema": {"month": {"type": "string"}},
        "layout_config": {"template": "monthly"},
    }


def snapshot_payload(
    metric_key: str, *, source_module: str = "orders"
) -> dict[str, object]:
    return {
        "metric_key": metric_key,
        "metric_name": f"Metric {metric_key}",
        "source_module": source_module,
        "entity_type": "tenant",
        "entity_id": "global",
        "period": AnalyticsSnapshotPeriod.DAILY.value,
        "status": AnalyticsSnapshotStatus.READY.value,
        "value": {"count": 100},
        "dimensions": {"region": "global"},
        "period_start": None,
        "period_end": None,
        "failure_reason": None,
    }


def test_health_route_uses_service(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "module": "reporting_analytics"}


def test_dashboard_routes_persist_list_filter_and_lookup_by_id_and_uuid(
    client: TestClient,
) -> None:
    first = client.post(f"{BASE_URL}/dashboards", json=dashboard_payload("ops-main"))
    second = client.post(
        f"{BASE_URL}/dashboards",
        json=dashboard_payload("finance-main", category="finance"),
    )

    assert first.status_code == 201
    assert second.status_code == 201
    first_body = first.json()
    assert first_body["code"] == "ops-main"
    assert first_body["dashboard_uuid"]

    filtered = client.get(f"{BASE_URL}/dashboards", params={"category": "operations"})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert [item["id"] for item in filtered.json()["items"]] == [first_body["id"]]

    by_id = client.get(f"{BASE_URL}/dashboards/{first_body['id']}")
    by_uuid = client.get(f"{BASE_URL}/dashboards/uuid/{first_body['dashboard_uuid']}")
    assert by_id.status_code == 200
    assert by_uuid.status_code == 200
    assert by_id.json() == by_uuid.json() == first_body


def test_report_and_run_routes_persist_filter_and_lookup(client: TestClient) -> None:
    report_response = client.post(
        f"{BASE_URL}/reports", json=report_payload("monthly-ops")
    )
    assert report_response.status_code == 201
    report = report_response.json()

    reports = client.get(f"{BASE_URL}/reports", params={"source_module": "orders"})
    assert reports.status_code == 200
    assert reports.json()["total"] == 1
    assert reports.json()["items"][0]["report_uuid"] == report["report_uuid"]

    run_payload = {
        "report_definition_id": report["id"],
        "requested_by_user_id": None,
        "file_object_id": None,
        "status": ReportRunStatus.QUEUED.value,
        "output_format": ReportOutputFormat.XLSX.value,
        "parameters": {"month": "2026-07"},
        "result_summary": None,
        "row_count": 0,
        "started_at": None,
        "completed_at": None,
        "failed_at": None,
        "failure_reason": None,
    }
    run_response = client.post(f"{BASE_URL}/runs", json=run_payload)
    assert run_response.status_code == 201
    run = run_response.json()

    runs = client.get(f"{BASE_URL}/runs", params={"report_definition_id": report["id"]})
    assert runs.status_code == 200
    assert runs.json()["total"] == 1
    assert runs.json()["items"][0]["run_uuid"] == run["run_uuid"]
    assert client.get(f"{BASE_URL}/runs/uuid/{run['run_uuid']}").json() == run


def test_snapshot_routes_persist_filter_and_lookup(client: TestClient) -> None:
    response = client.post(
        f"{BASE_URL}/snapshots", json=snapshot_payload("orders.total")
    )

    assert response.status_code == 201
    snapshot = response.json()
    assert snapshot["value"] == {"count": 100}

    filtered = client.get(
        f"{BASE_URL}/snapshots", params={"metric_key": "orders.total"}
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["snapshot_uuid"] == snapshot["snapshot_uuid"]
    assert client.get(f"{BASE_URL}/snapshots/{snapshot['id']}").json() == snapshot


def test_missing_records_and_invalid_payload_return_errors(client: TestClient) -> None:
    assert client.get(f"{BASE_URL}/dashboards/999").status_code == 404
    assert client.get(f"{BASE_URL}/reports/999").status_code == 404
    assert client.get(f"{BASE_URL}/runs/999").status_code == 404
    assert client.get(f"{BASE_URL}/snapshots/999").status_code == 404

    invalid_dashboard = client.post(
        f"{BASE_URL}/dashboards",
        json={**dashboard_payload(""), "name": ""},
    )
    invalid_run = client.post(
        f"{BASE_URL}/runs",
        json={"report_definition_id": 1, "row_count": -1},
    )

    assert invalid_dashboard.status_code == 422
    assert invalid_run.status_code == 422
