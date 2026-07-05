from __future__ import annotations

from collections.abc import Generator
from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.audit_log.models import AuditLogEvent


BASE_URL = "/api/v1/audit-log"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="audit-api-business-admin",
            full_name="Audit API Business Admin",
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


def create_test_user(db_session: Session, username: str) -> User:
    user = User(
        username=username,
        full_name="Audit API Business User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_audit_event(
    client: TestClient,
    *,
    event_type: str = "document.created",
    entity_type: str | None = "document",
    entity_id: str | None = "DOC-API-001",
    actor_user_id: int | None = None,
    actor_username: str | None = "audit-api-business-user",
    action: str = "create",
    status: str = "success",
    request_id: str | None = "request-api-001",
    correlation_id: str | None = "correlation-api-docs",
    payload: dict[str, object] | None = None,
    before_state: dict[str, object] | None = None,
    after_state: dict[str, object] | None = None,
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/events",
        json={
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "actor_user_id": actor_user_id,
            "actor_username": actor_username,
            "action": action,
            "status": status,
            "ip_address": "127.0.0.1",
            "user_agent": "pytest-audit-api-business",
            "request_id": request_id,
            "correlation_id": correlation_id,
            "payload": payload or {"source": "api-business-test"},
            "before_state": before_state,
            "after_state": after_state,
        },
    )

    assert response.status_code == 201
    return response.json()


def set_created_at(
    db_session: Session,
    event_id: int,
    created_at: datetime,
) -> None:
    event = db_session.get(AuditLogEvent, event_id)
    assert event is not None
    event.created_at = created_at
    db_session.flush()


def assert_audit_event_shape(audit_event: dict[str, object]) -> None:
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


def test_audit_log_event_create_detail_uuid_lookup_and_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    actor = create_test_user(db_session, "audit-api-business-actor")

    created_event = create_audit_event(
        client,
        event_type="document.updated",
        entity_type="document",
        entity_id="DOC-API-JSON",
        actor_user_id=actor.id,
        actor_username=actor.username,
        action="update",
        status="success",
        request_id="request-api-json",
        correlation_id="correlation-api-json",
        payload={
            "document_number": "DOC-API-JSON",
            "changes": ["title", "status"],
        },
        before_state={"title": "Draft", "status": "draft"},
        after_state={"title": "Approved", "status": "active"},
    )

    assert_audit_event_shape(created_event)
    assert isinstance(created_event["id"], int)
    assert isinstance(created_event["event_uuid"], str)
    assert created_event["event_type"] == "document.updated"
    assert created_event["payload"] == {
        "document_number": "DOC-API-JSON",
        "changes": ["title", "status"],
    }
    assert created_event["before_state"] == {"title": "Draft", "status": "draft"}
    assert created_event["after_state"] == {"title": "Approved", "status": "active"}
    assert isinstance(created_event["created_at"], str)

    persisted_event = db_session.get(AuditLogEvent, created_event["id"])
    assert persisted_event is not None
    assert persisted_event.event_type == "document.updated"
    assert persisted_event.payload == created_event["payload"]

    detail_response = client.get(f"{BASE_URL}/events/{created_event['id']}")
    uuid_response = client.get(
        f"{BASE_URL}/events/uuid/{created_event['event_uuid']}",
    )
    repeat_uuid_response = client.get(
        f"{BASE_URL}/events/uuid/{created_event['event_uuid']}",
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == created_event
    assert uuid_response.status_code == 200
    assert uuid_response.json() == created_event
    assert repeat_uuid_response.status_code == 200
    assert repeat_uuid_response.json()["id"] == created_event["id"]
    assert repeat_uuid_response.json()["event_uuid"] == created_event["event_uuid"]


def test_audit_log_list_filters_ordering_pagination_and_date_range(
    client: TestClient,
    db_session: Session,
) -> None:
    actor = create_test_user(db_session, "audit-api-filter-actor")
    other_actor = create_test_user(db_session, "audit-api-filter-other")

    first_event = create_audit_event(
        client,
        event_type="document.created",
        entity_type="document",
        entity_id="DOC-API-FILTER",
        actor_user_id=actor.id,
        actor_username=actor.username,
        action="create",
        status="success",
        request_id="request-api-filter-001",
        correlation_id="correlation-api-docs",
        payload={"step": 1},
    )
    second_event = create_audit_event(
        client,
        event_type="document.updated",
        entity_type="document",
        entity_id="DOC-API-FILTER",
        actor_user_id=actor.id,
        actor_username=actor.username,
        action="update",
        status="failure",
        request_id="request-api-filter-002",
        correlation_id="correlation-api-docs",
        payload={"step": 2},
    )
    third_event = create_audit_event(
        client,
        event_type="user.logged_in",
        entity_type="user",
        entity_id=str(other_actor.id),
        actor_user_id=other_actor.id,
        actor_username=other_actor.username,
        action="login",
        status="success",
        request_id="request-api-filter-003",
        correlation_id="correlation-api-auth",
        payload={"step": 3},
    )

    set_created_at(
        db_session,
        int(first_event["id"]),
        datetime(2026, 7, 5, 9, 0, 0),
    )
    set_created_at(
        db_session,
        int(second_event["id"]),
        datetime(2026, 7, 5, 10, 0, 0),
    )
    set_created_at(
        db_session,
        int(third_event["id"]),
        datetime(2026, 7, 5, 11, 0, 0),
    )

    list_response = client.get(f"{BASE_URL}/events")
    page_response = client.get(f"{BASE_URL}/events", params={"limit": 1, "offset": 1})
    entity_type_response = client.get(
        f"{BASE_URL}/events",
        params={"entity_type": "document"},
    )
    entity_id_response = client.get(
        f"{BASE_URL}/events",
        params={"entity_id": "DOC-API-FILTER"},
    )
    actor_response = client.get(
        f"{BASE_URL}/events",
        params={"actor_user_id": actor.id},
    )
    action_response = client.get(f"{BASE_URL}/events", params={"action": "update"})
    status_response = client.get(f"{BASE_URL}/events", params={"status": "failure"})
    request_response = client.get(
        f"{BASE_URL}/events",
        params={"request_id": "request-api-filter-003"},
    )
    correlation_response = client.get(
        f"{BASE_URL}/events",
        params={"correlation_id": "correlation-api-docs"},
    )
    date_range_response = client.get(
        f"{BASE_URL}/events",
        params={
            "created_from": "2026-07-05T10:00:00",
            "created_to": "2026-07-05T11:00:00",
        },
    )
    missing_filter_response = client.get(
        f"{BASE_URL}/events",
        params={"entity_type": "missing"},
    )

    assert list_response.status_code == 200
    list_body = list_response.json()
    assert set(list_body) == {"items", "total", "limit", "offset"}
    assert list_body["total"] == 3
    assert list_body["limit"] == 100
    assert list_body["offset"] == 0
    assert [event["id"] for event in list_body["items"]] == [
        third_event["id"],
        second_event["id"],
        first_event["id"],
    ]
    assert all(
        set(event) == set(list_body["items"][0])
        for event in list_body["items"]
    )

    assert page_response.status_code == 200
    assert page_response.json()["total"] == 3
    assert page_response.json()["limit"] == 1
    assert page_response.json()["offset"] == 1
    assert [event["id"] for event in page_response.json()["items"]] == [
        second_event["id"],
    ]

    assert entity_type_response.status_code == 200
    assert [event["id"] for event in entity_type_response.json()["items"]] == [
        second_event["id"],
        first_event["id"],
    ]
    assert entity_type_response.json()["total"] == 2

    assert entity_id_response.status_code == 200
    assert [event["id"] for event in entity_id_response.json()["items"]] == [
        second_event["id"],
        first_event["id"],
    ]
    assert actor_response.status_code == 200
    assert [event["id"] for event in actor_response.json()["items"]] == [
        second_event["id"],
        first_event["id"],
    ]
    assert action_response.status_code == 200
    assert [event["id"] for event in action_response.json()["items"]] == [
        second_event["id"],
    ]
    assert status_response.status_code == 200
    assert [event["id"] for event in status_response.json()["items"]] == [
        second_event["id"],
    ]
    assert request_response.status_code == 200
    assert [event["id"] for event in request_response.json()["items"]] == [
        third_event["id"],
    ]
    assert correlation_response.status_code == 200
    assert [event["id"] for event in correlation_response.json()["items"]] == [
        second_event["id"],
        first_event["id"],
    ]
    assert date_range_response.status_code == 200
    assert [event["id"] for event in date_range_response.json()["items"]] == [
        third_event["id"],
        second_event["id"],
    ]
    assert missing_filter_response.status_code == 200
    assert missing_filter_response.json() == {
        "items": [],
        "total": 0,
        "limit": 100,
        "offset": 0,
    }


def test_audit_log_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    missing_get_response = client.get(f"{BASE_URL}/events/999")
    missing_uuid_response = client.get(f"{BASE_URL}/events/uuid/{uuid4()}")
    invalid_id_response = client.get(f"{BASE_URL}/events/not-an-int")
    invalid_uuid_response = client.get(f"{BASE_URL}/events/uuid/not-a-uuid")
    create_validation_response = client.post(
        f"{BASE_URL}/events",
        json={"event_type": "document.changed"},
    )
    invalid_payload_response = client.post(
        f"{BASE_URL}/events",
        json={
            "event_type": "document.changed",
            "action": "update",
            "payload": ["not", "a", "dict"],
        },
    )
    invalid_query_response = client.get(f"{BASE_URL}/events", params={"limit": 0})
    invalid_offset_response = client.get(f"{BASE_URL}/events", params={"offset": -1})
    invalid_actor_response = client.get(
        f"{BASE_URL}/events",
        params={"actor_user_id": "not-an-int"},
    )
    invalid_date_response = client.get(
        f"{BASE_URL}/events",
        params={"created_from": "not-a-date"},
    )

    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {"detail": "Audit log event not found"}
    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {"detail": "Audit log event not found"}
    assert invalid_id_response.status_code == 422
    assert invalid_uuid_response.status_code == 422
    assert create_validation_response.status_code == 422
    assert invalid_payload_response.status_code == 422
    assert invalid_query_response.status_code == 422
    assert invalid_offset_response.status_code == 422
    assert invalid_actor_response.status_code == 422
    assert invalid_date_response.status_code == 422
