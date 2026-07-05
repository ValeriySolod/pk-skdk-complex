from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.notifications.models import (
    Notification,
    NotificationChannel,
    NotificationDelivery,
    NotificationDeliveryStatus,
    NotificationPriority,
    NotificationProvider,
    NotificationStatus,
    NotificationType,
)


BASE_URL = "/api/v1/notifications"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="notifications-api-business-admin",
            full_name="Notifications API Business Admin",
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


def notification_payload(
    *,
    recipient_user_id: int | None = None,
    actor_user_id: int | None = None,
    type: str = NotificationType.WORKFLOW.value,
    channel: str = NotificationChannel.IN_APP.value,
    priority: str = NotificationPriority.NORMAL.value,
    status: str = NotificationStatus.PENDING.value,
    title: str = "Quality task assigned",
    body: str | None = "A document needs your review.",
    payload: dict[str, object] | None = None,
    entity_type: str | None = "document",
    entity_id: str | None = "DOC-NOTIFY-001",
    correlation_id: str | None = "corr-notify-001",
    request_id: str | None = "req-notify-001",
    scheduled_at: str | None = None,
    sent_at: str | None = None,
    read_at: str | None = None,
    dismissed_at: str | None = None,
    failed_at: str | None = None,
    failure_reason: str | None = None,
) -> dict[str, object | None]:
    return {
        "recipient_user_id": recipient_user_id,
        "actor_user_id": actor_user_id,
        "type": type,
        "channel": channel,
        "priority": priority,
        "status": status,
        "title": title,
        "body": body,
        "payload": payload if payload is not None else {"document_number": "DOC-001"},
        "entity_type": entity_type,
        "entity_id": entity_id,
        "correlation_id": correlation_id,
        "request_id": request_id,
        "scheduled_at": scheduled_at,
        "sent_at": sent_at,
        "read_at": read_at,
        "dismissed_at": dismissed_at,
        "failed_at": failed_at,
        "failure_reason": failure_reason,
    }


def delivery_payload(
    notification_id: int,
    *,
    channel: str = NotificationChannel.IN_APP.value,
    provider: str | None = NotificationProvider.INTERNAL.value,
    provider_message_id: str | None = "internal-msg-001",
    status: str = NotificationDeliveryStatus.PENDING.value,
    attempt_count: int = 0,
    last_attempt_at: str | None = None,
    delivered_at: str | None = None,
    failed_at: str | None = None,
    failure_reason: str | None = None,
    provider_response: dict[str, object] | None = None,
) -> dict[str, object | None]:
    return {
        "notification_id": notification_id,
        "channel": channel,
        "provider": provider,
        "provider_message_id": provider_message_id,
        "status": status,
        "attempt_count": attempt_count,
        "last_attempt_at": last_attempt_at,
        "delivered_at": delivered_at,
        "failed_at": failed_at,
        "failure_reason": failure_reason,
        "provider_response": provider_response
        if provider_response is not None
        else {"accepted": True},
    }


def create_notification(client: TestClient, **overrides: object) -> dict[str, object]:
    response = client.post(BASE_URL, json=notification_payload(**overrides))

    assert response.status_code == 201
    return response.json()


def create_delivery(
    client: TestClient,
    notification_id: int,
    **overrides: object,
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/deliveries",
        json=delivery_payload(notification_id, **overrides),
    )

    assert response.status_code == 201
    return response.json()


def assert_notification_shape(notification: dict[str, object]) -> None:
    assert set(notification) == {
        "id",
        "notification_uuid",
        "recipient_user_id",
        "actor_user_id",
        "type",
        "channel",
        "priority",
        "status",
        "title",
        "body",
        "payload",
        "entity_type",
        "entity_id",
        "correlation_id",
        "request_id",
        "scheduled_at",
        "sent_at",
        "read_at",
        "dismissed_at",
        "failed_at",
        "failure_reason",
        "created_at",
        "updated_at",
        "deleted_at",
    }


def assert_delivery_shape(delivery: dict[str, object]) -> None:
    assert set(delivery) == {
        "id",
        "delivery_uuid",
        "notification_id",
        "channel",
        "provider",
        "provider_message_id",
        "status",
        "attempt_count",
        "last_attempt_at",
        "delivered_at",
        "failed_at",
        "failure_reason",
        "provider_response",
        "created_at",
        "updated_at",
    }


def assert_notification_list_ids(
    client: TestClient,
    expected_ids: list[int],
    *,
    expected_total: int | None = None,
    **params: object,
) -> None:
    response = client.get(BASE_URL, params=params)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "limit", "offset"}
    assert [item["id"] for item in body["items"]] == expected_ids
    assert body["total"] == (
        expected_total if expected_total is not None else len(expected_ids)
    )
    assert body["limit"] == params.get("limit", 100)
    assert body["offset"] == params.get("offset", 0)
    for item in body["items"]:
        assert_notification_shape(item)


def assert_delivery_list_ids(
    client: TestClient,
    expected_ids: list[int],
    *,
    expected_total: int | None = None,
    **params: object,
) -> None:
    response = client.get(f"{BASE_URL}/deliveries", params=params)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "limit", "offset"}
    assert [item["id"] for item in body["items"]] == expected_ids
    assert body["total"] == (
        expected_total if expected_total is not None else len(expected_ids)
    )
    assert body["limit"] == params.get("limit", 100)
    assert body["offset"] == params.get("offset", 0)
    for item in body["items"]:
        assert_delivery_shape(item)


def test_notification_create_read_list_uuid_lookup_and_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    created = create_notification(
        client,
        recipient_user_id=None,
        actor_user_id=None,
        channel=NotificationChannel.EMAIL.value,
        priority=NotificationPriority.HIGH.value,
        title="Procedure approval requested",
        payload={"document_number": "DOC-API-001", "revision": 2},
        entity_id="DOC-API-001",
    )

    assert_notification_shape(created)
    assert isinstance(created["id"], int)
    assert isinstance(created["notification_uuid"], str)
    assert created["title"] == "Procedure approval requested"
    assert created["channel"] == NotificationChannel.EMAIL.value
    assert created["priority"] == NotificationPriority.HIGH.value
    assert created["status"] == NotificationStatus.PENDING.value
    assert created["payload"] == {"document_number": "DOC-API-001", "revision": 2}
    assert created["deleted_at"] is None

    persisted_notification = db_session.get(Notification, created["id"])
    assert persisted_notification is not None
    assert str(persisted_notification.notification_uuid) == created["notification_uuid"]
    assert persisted_notification.payload == {
        "document_number": "DOC-API-001",
        "revision": 2,
    }

    detail_response = client.get(f"{BASE_URL}/{created['id']}")
    uuid_response = client.get(f"{BASE_URL}/uuid/{created['notification_uuid']}")

    assert detail_response.status_code == 200
    assert detail_response.json() == created
    assert uuid_response.status_code == 200
    assert uuid_response.json() == created
    assert_notification_list_ids(client, [created["id"]])


def test_notification_filters_pagination_count_and_soft_delete_visibility(
    client: TestClient,
    db_session: Session,
) -> None:
    first = create_notification(
        client,
        type=NotificationType.WORKFLOW.value,
        channel=NotificationChannel.IN_APP.value,
        priority=NotificationPriority.NORMAL.value,
        status=NotificationStatus.PENDING.value,
        title="Workflow notification",
        entity_type="document",
        entity_id="DOC-FILTER-001",
        correlation_id="corr-filter-001",
        request_id="req-filter-001",
    )
    second = create_notification(
        client,
        type=NotificationType.SECURITY.value,
        channel=NotificationChannel.EMAIL.value,
        priority=NotificationPriority.URGENT.value,
        status=NotificationStatus.READ.value,
        title="Security notification",
        entity_type="user",
        entity_id="42",
        correlation_id="corr-filter-002",
        request_id="req-filter-002",
        read_at="2026-07-05T12:00:00Z",
    )
    third = create_notification(
        client,
        type=NotificationType.REMINDER.value,
        channel=NotificationChannel.PUSH.value,
        priority=NotificationPriority.LOW.value,
        status=NotificationStatus.SCHEDULED.value,
        title="Scheduled reminder",
        entity_type="task",
        entity_id="TASK-001",
        scheduled_at="2026-07-06T09:30:00Z",
    )

    soft_deleted = db_session.get(Notification, third["id"])
    assert soft_deleted is not None
    soft_deleted.deleted_at = datetime(2026, 7, 5, 13, 0, tzinfo=UTC)
    db_session.commit()

    assert_notification_list_ids(client, [second["id"], first["id"]], expected_total=2)
    assert_notification_list_ids(
        client,
        [first["id"]],
        type=NotificationType.WORKFLOW.value,
    )
    assert_notification_list_ids(
        client,
        [second["id"]],
        channel=NotificationChannel.EMAIL.value,
    )
    assert_notification_list_ids(
        client,
        [second["id"]],
        priority=NotificationPriority.URGENT.value,
    )
    assert_notification_list_ids(
        client,
        [second["id"]],
        status=NotificationStatus.READ.value,
    )
    assert_notification_list_ids(
        client,
        [first["id"]],
        entity_type="document",
        entity_id="DOC-FILTER-001",
    )
    assert_notification_list_ids(
        client,
        [first["id"]],
        correlation_id="corr-filter-001",
        request_id="req-filter-001",
    )
    assert_notification_list_ids(
        client,
        [first["id"]],
        limit=1,
        offset=1,
        expected_total=2,
    )
    assert_notification_list_ids(
        client,
        [third["id"], second["id"], first["id"]],
        include_deleted=True,
        expected_total=3,
    )

    deleted_detail_response = client.get(f"{BASE_URL}/{third['id']}")
    deleted_uuid_response = client.get(f"{BASE_URL}/uuid/{third['notification_uuid']}")

    assert deleted_detail_response.status_code == 404
    assert deleted_detail_response.json() == {"detail": "Notification not found"}
    assert deleted_uuid_response.status_code == 404
    assert deleted_uuid_response.json() == {"detail": "Notification not found"}


def test_notification_api_validation_and_missing_entities(client: TestClient) -> None:
    missing_id_response = client.get(f"{BASE_URL}/999")
    missing_uuid_response = client.get(
        f"{BASE_URL}/uuid/33333333-3333-4333-8333-333333333333",
    )
    invalid_create_response = client.post(BASE_URL, json={"body": "Missing title"})
    invalid_empty_title_response = client.post(
        BASE_URL,
        json=notification_payload(title=""),
    )
    invalid_query_response = client.get(BASE_URL, params={"limit": 0})
    invalid_offset_response = client.get(BASE_URL, params={"offset": -1})
    invalid_uuid_response = client.get(f"{BASE_URL}/uuid/not-a-uuid")

    assert missing_id_response.status_code == 404
    assert missing_id_response.json() == {"detail": "Notification not found"}
    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {"detail": "Notification not found"}
    assert invalid_create_response.status_code == 422
    assert invalid_empty_title_response.status_code == 422
    assert invalid_query_response.status_code == 422
    assert invalid_offset_response.status_code == 422
    assert invalid_uuid_response.status_code == 422


def test_delivery_create_read_list_uuid_lookup_status_and_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    notification = create_notification(client, title="Delivery parent notification")
    created = create_delivery(
        client,
        notification["id"],
        channel=NotificationChannel.EMAIL.value,
        provider=NotificationProvider.SMTP.value,
        provider_message_id="smtp-msg-001",
        status=NotificationDeliveryStatus.SENT.value,
        attempt_count=1,
        last_attempt_at="2026-07-05T12:00:00Z",
        provider_response={"message_id": "smtp-msg-001", "accepted": True},
    )

    assert_delivery_shape(created)
    assert isinstance(created["id"], int)
    assert isinstance(created["delivery_uuid"], str)
    assert created["notification_id"] == notification["id"]
    assert created["channel"] == NotificationChannel.EMAIL.value
    assert created["provider"] == NotificationProvider.SMTP.value
    assert created["status"] == NotificationDeliveryStatus.SENT.value
    assert created["attempt_count"] == 1
    assert created["provider_response"] == {
        "message_id": "smtp-msg-001",
        "accepted": True,
    }

    persisted_delivery = db_session.get(NotificationDelivery, created["id"])
    assert persisted_delivery is not None
    assert str(persisted_delivery.delivery_uuid) == created["delivery_uuid"]
    assert persisted_delivery.provider_response == {
        "message_id": "smtp-msg-001",
        "accepted": True,
    }

    detail_response = client.get(f"{BASE_URL}/deliveries/{created['id']}")
    uuid_response = client.get(f"{BASE_URL}/deliveries/uuid/{created['delivery_uuid']}")

    assert detail_response.status_code == 200
    assert detail_response.json() == created
    assert uuid_response.status_code == 200
    assert uuid_response.json() == created
    assert_delivery_list_ids(client, [created["id"]])


def test_delivery_filters_pagination_and_count_consistency(client: TestClient) -> None:
    notification = create_notification(client, title="Delivery filter parent")
    first = create_delivery(
        client,
        notification["id"],
        channel=NotificationChannel.IN_APP.value,
        provider=NotificationProvider.INTERNAL.value,
        provider_message_id="internal-filter-001",
        status=NotificationDeliveryStatus.PENDING.value,
    )
    second = create_delivery(
        client,
        notification["id"],
        channel=NotificationChannel.EMAIL.value,
        provider=NotificationProvider.SMTP.value,
        provider_message_id="smtp-filter-001",
        status=NotificationDeliveryStatus.DELIVERED.value,
        attempt_count=1,
        delivered_at="2026-07-05T12:10:00Z",
    )
    third = create_delivery(
        client,
        notification["id"],
        channel=NotificationChannel.SMS.value,
        provider=NotificationProvider.SMS_GATEWAY.value,
        provider_message_id="sms-filter-001",
        status=NotificationDeliveryStatus.FAILED.value,
        attempt_count=2,
        failed_at="2026-07-05T12:15:00Z",
        failure_reason="Provider rejected message",
    )

    assert_delivery_list_ids(
        client,
        [third["id"], second["id"], first["id"]],
        expected_total=3,
    )
    assert_delivery_list_ids(
        client,
        [first["id"]],
        channel=NotificationChannel.IN_APP.value,
    )
    assert_delivery_list_ids(
        client,
        [second["id"]],
        provider=NotificationProvider.SMTP.value,
    )
    assert_delivery_list_ids(
        client,
        [third["id"]],
        status=NotificationDeliveryStatus.FAILED.value,
    )
    assert_delivery_list_ids(
        client,
        [second["id"]],
        provider_message_id="smtp-filter-001",
    )
    assert_delivery_list_ids(
        client,
        [third["id"], second["id"]],
        limit=2,
        offset=0,
        expected_total=3,
    )
    assert_delivery_list_ids(
        client,
        [second["id"]],
        delivered_from="2026-07-05T12:00:00Z",
        delivered_to="2026-07-05T12:20:00Z",
    )
    assert_delivery_list_ids(
        client,
        [third["id"]],
        failed_from="2026-07-05T12:00:00Z",
        failed_to="2026-07-05T12:20:00Z",
    )


def test_delivery_api_validation_and_missing_entities(client: TestClient) -> None:
    notification = create_notification(client, title="Delivery validation parent")

    missing_id_response = client.get(f"{BASE_URL}/deliveries/999")
    missing_uuid_response = client.get(
        f"{BASE_URL}/deliveries/uuid/44444444-4444-4444-8444-444444444444",
    )
    invalid_create_response = client.post(
        f"{BASE_URL}/deliveries",
        json={"status": "pending"},
    )
    invalid_attempt_response = client.post(
        f"{BASE_URL}/deliveries",
        json=delivery_payload(notification["id"], attempt_count=-1),
    )
    invalid_query_response = client.get(f"{BASE_URL}/deliveries", params={"limit": 0})
    invalid_offset_response = client.get(
        f"{BASE_URL}/deliveries",
        params={"offset": -1},
    )
    invalid_uuid_response = client.get(f"{BASE_URL}/deliveries/uuid/not-a-uuid")

    assert missing_id_response.status_code == 404
    assert missing_id_response.json() == {"detail": "Notification delivery not found"}
    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {"detail": "Notification delivery not found"}
    assert invalid_create_response.status_code == 422
    assert invalid_attempt_response.status_code == 422
    assert invalid_query_response.status_code == 422
    assert invalid_offset_response.status_code == 422
    assert invalid_uuid_response.status_code == 422
