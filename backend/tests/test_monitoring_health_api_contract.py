"""Focused database-backed API contracts for Monitoring & Health."""
from collections.abc import Iterator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User

BASE_URL = "/api/v1/monitoring_health"

@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    original = app.dependency_overrides.copy()
    def db() -> Iterator[Session]: yield db_session
    def user() -> User:
        return User(id=1, username="monitor", full_name="Monitor", password_hash="unused", role="test", is_active=True)
    app.dependency_overrides[get_db] = db
    app.dependency_overrides[get_current_user] = user
    with TestClient(app) as result: yield result
    app.dependency_overrides = original

def test_routes_require_authentication(db_session: Session) -> None:
    original = app.dependency_overrides.copy()
    def db() -> Iterator[Session]: yield db_session
    app.dependency_overrides[get_db] = db
    app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as client:
        assert client.get(f"{BASE_URL}/health").status_code == 401
    app.dependency_overrides = original

def test_health_and_route_registration(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "module": "monitoring_health"}
    paths = {route.path for route in app.routes}
    assert f"{BASE_URL}/health-checks" in paths
    assert f"{BASE_URL}/metrics" in paths
    assert f"{BASE_URL}/incidents" in paths

@pytest.mark.parametrize("path,payload,uuid_field,fields,filter_query", [
    ("health-checks", {"component":"database", "status":"healthy", "response_time_ms":4.2, "details":{"probe":"sql"}}, "record_uuid", {"component","status","details","checked_at","created_at"}, "component=database"),
    ("metrics", {"metric_name":"cpu.usage", "category":"system", "source":"node-1", "value":42.5, "unit":"percent", "labels":{"host":"node-1"}}, "metric_uuid", {"metric_name","category","value","labels","recorded_at"}, "source=node-1"),
    ("incidents", {"title":"Database latency", "severity":"high", "source":"monitor", "component":"database", "metadata_json":{"trace":"abc"}}, "incident_uuid", {"title","severity","status","metadata_json","detected_at","updated_at"}, "severity=high"),
])
def test_create_list_id_uuid_filter_and_persistence(client: TestClient, db_session: Session, path: str, payload: dict[str, object], uuid_field: str, fields: set[str], filter_query: str) -> None:
    created = client.post(f"{BASE_URL}/{path}", json=payload)
    assert created.status_code == 201, created.text
    item = created.json(); assert {"id", uuid_field, *fields} <= set(item)
    assert client.get(f"{BASE_URL}/{path}/{item['id']}").json()[uuid_field] == item[uuid_field]
    assert client.get(f"{BASE_URL}/{path}/uuid/{item[uuid_field]}").json()["id"] == item["id"]
    listed = client.get(f"{BASE_URL}/{path}?{filter_query}&limit=1&offset=0").json()
    assert listed["total"] == 1 and listed["limit"] == 1 and listed["offset"] == 0
    assert listed["items"][0]["id"] == item["id"]
    assert db_session.get({"health-checks": __import__('app.modules.monitoring_health.models', fromlist=['HealthCheckRecord']).HealthCheckRecord, "metrics": __import__('app.modules.monitoring_health.models', fromlist=['MonitoringMetric']).MonitoringMetric, "incidents": __import__('app.modules.monitoring_health.models', fromlist=['SystemIncident']).SystemIncident}[path], item["id"]) is not None

def test_incident_lifecycle_missing_and_invalid_contracts(client: TestClient) -> None:
    incident = client.post(f"{BASE_URL}/incidents", json={"title":"Outage"}).json()
    updated = client.patch(f"{BASE_URL}/incidents/{incident['id']}/status", json={"status":"resolved", "resolution_summary":"Recovered"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "resolved" and updated.json()["resolved_at"] is not None
    assert client.get(f"{BASE_URL}/incidents/999999").status_code == 404
    assert client.get(f"{BASE_URL}/metrics/999999").status_code == 404
    assert client.post(f"{BASE_URL}/health-checks", json={"component":"", "status":"invalid"}).status_code == 422
    assert client.post(f"{BASE_URL}/metrics", json={"metric_name":"cpu"}).status_code == 422
    assert client.post(f"{BASE_URL}/incidents", json={"title":"", "severity":"urgent"}).status_code == 422


@pytest.mark.parametrize(
    "path,payload,json_field,expected",
    [
        ("health-checks", {"component": "cache", "details": ["redis", 3, True]}, "details", ["redis", 3, True]),
        ("metrics", {"metric_name": "feature.enabled", "value": 1, "labels": True}, "labels", True),
        ("metrics", {"metric_name": "build.version", "value": 1, "details": "2026.07"}, "details", "2026.07"),
        ("incidents", {"title": "Worker backlog", "metadata_json": 17}, "metadata_json", 17),
    ],
)
def test_json_fields_accept_and_persist_non_object_top_level_values(
    client: TestClient,
    path: str,
    payload: dict[str, object],
    json_field: str,
    expected: object,
) -> None:
    created = client.post(f"{BASE_URL}/{path}", json=payload)
    assert created.status_code == 201, created.text
    assert created.json()[json_field] == expected

    persisted = client.get(f"{BASE_URL}/{path}/{created.json()['id']}")
    assert persisted.status_code == 200
    assert persisted.json()[json_field] == expected


def test_full_incident_update_persists_supported_fields(client: TestClient) -> None:
    created = client.post(
        f"{BASE_URL}/incidents",
        json={"title": "Queue delay", "severity": "medium"},
    ).json()

    updated = client.patch(
        f"{BASE_URL}/incidents/{created['id']}",
        json={
            "title": "Queue delay investigated",
            "severity": "high",
            "description": "Backlog confirmed",
            "metadata_json": ["queue", "worker"],
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "Queue delay investigated"
    assert updated.json()["severity"] == "high"
    assert updated.json()["description"] == "Backlog confirmed"
    assert updated.json()["metadata_json"] == ["queue", "worker"]

    persisted = client.get(f"{BASE_URL}/incidents/{created['id']}")
    assert persisted.status_code == 200
    assert persisted.json()["title"] == "Queue delay investigated"
    assert persisted.json()["severity"] == "high"
    assert persisted.json()["description"] == "Backlog confirmed"
    assert persisted.json()["metadata_json"] == ["queue", "worker"]
