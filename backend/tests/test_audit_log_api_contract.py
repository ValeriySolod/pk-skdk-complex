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
from app.modules.audit_log import routes as audit_routes


BASE_URL = "/api/v1/audit-log"


class FakeSession:
    def commit(self) -> None:
        pass

    def refresh(self, _: object) -> None:
        pass


class FakeAuditLogService:
    def __init__(self) -> None:
        self.now = datetime(2026, 7, 5, 12, 0, tzinfo=UTC)
        self.events: dict[int, SimpleNamespace] = {
            1: SimpleNamespace(
                id=1,
                event_uuid=UUID("11111111-1111-4111-8111-111111111111"),
                event_type="document.changed",
                entity_type="document",
                entity_id="DOC-001",
                actor_user_id=1,
                actor_username="audit-contract-admin",
                action="update",
                status="success",
                ip_address="127.0.0.1",
                user_agent="contract-test",
                request_id="req-1",
                correlation_id="corr-1",
                payload={"field": "status"},
                before_state={"status": "draft"},
                after_state={"status": "active"},
                created_at=self.now,
            ),
        }
        self.next_event_id = 2
        self.last_list_filters: dict[str, object] | None = None
        self.last_count_filters: dict[str, object] | None = None

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def list_events(self, **filters: object) -> list[SimpleNamespace]:
        self.last_list_filters = filters
        return list(self.events.values())

    def count_events(self, **filters: object) -> int:
        self.last_count_filters = filters
        return len(self.events)

    def create_event(self, audit_event: object) -> SimpleNamespace:
        created_event = SimpleNamespace(
            id=self.next_event_id,
            event_uuid=uuid4(),
            created_at=self.now,
            event_type=getattr(audit_event, "event_type"),
            entity_type=getattr(audit_event, "entity_type"),
            entity_id=getattr(audit_event, "entity_id"),
            actor_user_id=getattr(audit_event, "actor_user_id"),
            actor_username=getattr(audit_event, "actor_username"),
            action=getattr(audit_event, "action"),
            status=getattr(audit_event, "status"),
            ip_address=getattr(audit_event, "ip_address"),
            user_agent=getattr(audit_event, "user_agent"),
            request_id=getattr(audit_event, "request_id"),
            correlation_id=getattr(audit_event, "correlation_id"),
            payload=getattr(audit_event, "payload"),
            before_state=getattr(audit_event, "before_state"),
            after_state=getattr(audit_event, "after_state"),
        )
        self.events[created_event.id] = created_event
        self.next_event_id += 1
        return created_event

    def get_event(self, audit_event_id: int) -> SimpleNamespace | None:
        return self.events.get(audit_event_id)

    def get_event_by_uuid(self, event_uuid: UUID) -> SimpleNamespace | None:
        return next(
            (
                audit_event
                for audit_event in self.events.values()
                if audit_event.event_uuid == event_uuid
            ),
            None,
        )


@pytest.fixture()
def service() -> FakeAuditLogService:
    return FakeAuditLogService()


@pytest.fixture()
def client(
    monkeypatch: pytest.MonkeyPatch,
    service: FakeAuditLogService,
) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()
    original_get_service = audit_routes.get_audit_log_service

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="audit-contract-admin",
            full_name="Audit Contract Admin",
            password_hash="not-used",
            role="test",
            is_active=True,
        )

    def override_get_db() -> Generator[FakeSession, None, None]:
        yield FakeSession()

    def override_get_service() -> FakeAuditLogService:
        return service

    monkeypatch.setattr(
        audit_routes,
        "get_audit_log_service",
        lambda db=None: service,
    )
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[original_get_service] = override_get_service

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides = original_overrides


def assert_audit_event_contract(audit_event: dict[str, object]) -> None:
    assert set(audit_event) == {
        "id",
        "event_uuid",
        "event_type",
        "entity_type",
        "entity_id",
        "actor_user_id",
        "actor_username",
        "action",
        "status",
        "ip_address",
        "user_agent",
        "request_id",
        "correlation_id",
        "payload",
        "before_state",
        "after_state",
        "created_at",
    }


def test_audit_log_health_contract(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_audit_log_list_exposes_response_and_query_contract(
    client: TestClient,
    service: FakeAuditLogService,
) -> None:
    response = client.get(
        f"{BASE_URL}/events",
        params={
            "actor_user_id": 1,
            "actor_username": "audit-contract-admin",
            "event_type": "document.changed",
            "action": "update",
            "status": "success",
            "entity_type": "document",
            "entity_id": "DOC-001",
            "request_id": "req-1",
            "correlation_id": "corr-1",
            "created_from": "2026-07-05T00:00:00Z",
            "created_to": "2026-07-06T00:00:00Z",
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
    assert_audit_event_contract(body["items"][0])
    assert service.last_list_filters is not None
    assert service.last_list_filters["limit"] == 25
    assert service.last_list_filters["offset"] == 5
    assert service.last_list_filters["event_type"] == "document.changed"
    assert service.last_count_filters is not None
    assert "limit" not in service.last_count_filters
    assert "offset" not in service.last_count_filters


def test_audit_log_create_and_get_contract(client: TestClient) -> None:
    create_response = client.post(
        f"{BASE_URL}/events",
        json={
            "event_type": "document.created",
            "entity_type": "document",
            "entity_id": "DOC-002",
            "actor_user_id": 1,
            "actor_username": "audit-contract-admin",
            "action": "create",
            "status": "success",
            "ip_address": "127.0.0.1",
            "user_agent": "contract-test",
            "request_id": "req-2",
            "correlation_id": "corr-2",
            "payload": {"document_number": "DOC-002"},
            "before_state": None,
            "after_state": {"status": "draft"},
        },
    )
    detail_response = client.get(f"{BASE_URL}/events/2")

    assert create_response.status_code == 201
    created_event = create_response.json()
    assert_audit_event_contract(created_event)
    assert created_event["event_type"] == "document.created"
    assert created_event["payload"] == {"document_number": "DOC-002"}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == 2


def test_audit_log_uuid_detail_contract(client: TestClient) -> None:
    response = client.get(
        f"{BASE_URL}/events/uuid/11111111-1111-4111-8111-111111111111",
    )

    assert response.status_code == 200
    assert response.json()["event_uuid"] == "11111111-1111-4111-8111-111111111111"


def test_audit_log_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    missing_get_response = client.get(f"{BASE_URL}/events/999")
    missing_uuid_response = client.get(
        f"{BASE_URL}/events/uuid/22222222-2222-4222-8222-222222222222",
    )
    create_validation_response = client.post(
        f"{BASE_URL}/events",
        json={"event_type": "document.changed"},
    )
    query_validation_response = client.get(f"{BASE_URL}/events?limit=0")

    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {"detail": "Audit log event not found"}
    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {"detail": "Audit log event not found"}
    assert create_validation_response.status_code == 422
    assert query_validation_response.status_code == 422
