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
from app.modules.notifications import routes as notification_routes


BASE_URL = "/api/v1/notifications"


class FakeSession:
    def commit(self) -> None:
        pass

    def refresh(self, _: object) -> None:
        pass


class FakeNotificationsService:
    def __init__(self) -> None:
        self.now = datetime(2026, 7, 5, 12, 0, tzinfo=UTC)
        self.notifications: dict[int, SimpleNamespace] = {
            1: SimpleNamespace(
                id=1,
                notification_uuid=UUID("11111111-1111-4111-8111-111111111111"),
                recipient_user_id=1,
                actor_user_id=None,
                type="system",
                channel="in_app",
                priority="normal",
                status="pending",
                title="Quality review assigned",
                body="A document needs your review.",
                payload={"document_number": "DOC-001"},
                entity_type="document",
                entity_id="DOC-001",
                correlation_id="corr-001",
                request_id="req-001",
                scheduled_at=None,
                sent_at=None,
                read_at=None,
                dismissed_at=None,
                failed_at=None,
                failure_reason=None,
                created_at=self.now,
                updated_at=self.now,
                deleted_at=None,
            ),
        }
        self.deliveries: dict[int, SimpleNamespace] = {
            1: SimpleNamespace(
                id=1,
                delivery_uuid=UUID("22222222-2222-4222-8222-222222222222"),
                notification_id=1,
                channel="in_app",
                provider="internal",
                provider_message_id="msg-001",
                status="pending",
                attempt_count=0,
                last_attempt_at=None,
                delivered_at=None,
                failed_at=None,
                failure_reason=None,
                provider_response={"accepted": True},
                created_at=self.now,
                updated_at=self.now,
            ),
        }
        self.next_notification_id = 2
        self.next_delivery_id = 2
        self.last_notification_list_filters: dict[str, object] | None = None
        self.last_notification_count_filters: dict[str, object] | None = None
        self.last_delivery_list_filters: dict[str, object] | None = None
        self.last_delivery_count_filters: dict[str, object] | None = None

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def list_notifications(self, **filters: object) -> list[SimpleNamespace]:
        self.last_notification_list_filters = filters
        return list(self.notifications.values())

    def count_notifications(self, **filters: object) -> int:
        self.last_notification_count_filters = filters
        return len(self.notifications)

    def create_notification(self, notification: object) -> SimpleNamespace:
        created = SimpleNamespace(
            id=self.next_notification_id,
            notification_uuid=uuid4(),
            created_at=self.now,
            updated_at=self.now,
            deleted_at=None,
            recipient_user_id=getattr(notification, "recipient_user_id"),
            actor_user_id=getattr(notification, "actor_user_id"),
            type=getattr(notification, "type"),
            channel=getattr(notification, "channel"),
            priority=getattr(notification, "priority"),
            status=getattr(notification, "status"),
            title=getattr(notification, "title"),
            body=getattr(notification, "body"),
            payload=getattr(notification, "payload"),
            entity_type=getattr(notification, "entity_type"),
            entity_id=getattr(notification, "entity_id"),
            correlation_id=getattr(notification, "correlation_id"),
            request_id=getattr(notification, "request_id"),
            scheduled_at=getattr(notification, "scheduled_at"),
            sent_at=getattr(notification, "sent_at"),
            read_at=getattr(notification, "read_at"),
            dismissed_at=getattr(notification, "dismissed_at"),
            failed_at=getattr(notification, "failed_at"),
            failure_reason=getattr(notification, "failure_reason"),
        )
        self.notifications[created.id] = created
        self.next_notification_id += 1
        return created

    def get_notification(self, notification_id: int) -> SimpleNamespace | None:
        return self.notifications.get(notification_id)

    def get_notification_by_uuid(
        self,
        notification_uuid: UUID,
    ) -> SimpleNamespace | None:
        return next(
            (
                notification
                for notification in self.notifications.values()
                if notification.notification_uuid == notification_uuid
            ),
            None,
        )

    def list_deliveries(self, **filters: object) -> list[SimpleNamespace]:
        self.last_delivery_list_filters = filters
        return list(self.deliveries.values())

    def count_deliveries(self, **filters: object) -> int:
        self.last_delivery_count_filters = filters
        return len(self.deliveries)

    def create_delivery(self, delivery: object) -> SimpleNamespace:
        created = SimpleNamespace(
            id=self.next_delivery_id,
            delivery_uuid=uuid4(),
            created_at=self.now,
            updated_at=self.now,
            notification_id=getattr(delivery, "notification_id"),
            channel=getattr(delivery, "channel"),
            provider=getattr(delivery, "provider"),
            provider_message_id=getattr(delivery, "provider_message_id"),
            status=getattr(delivery, "status"),
            attempt_count=getattr(delivery, "attempt_count"),
            last_attempt_at=getattr(delivery, "last_attempt_at"),
            delivered_at=getattr(delivery, "delivered_at"),
            failed_at=getattr(delivery, "failed_at"),
            failure_reason=getattr(delivery, "failure_reason"),
            provider_response=getattr(delivery, "provider_response"),
        )
        self.deliveries[created.id] = created
        self.next_delivery_id += 1
        return created

    def get_delivery(self, delivery_id: int) -> SimpleNamespace | None:
        return self.deliveries.get(delivery_id)

    def get_delivery_by_uuid(
        self,
        delivery_uuid: UUID,
    ) -> SimpleNamespace | None:
        return next(
            (
                delivery
                for delivery in self.deliveries.values()
                if delivery.delivery_uuid == delivery_uuid
            ),
            None,
        )


@pytest.fixture()
def service() -> FakeNotificationsService:
    return FakeNotificationsService()


@pytest.fixture()
def client(
    monkeypatch: pytest.MonkeyPatch,
    service: FakeNotificationsService,
) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()
    original_get_service = notification_routes.get_notifications_service

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="notifications-contract-admin",
            full_name="Notifications Contract Admin",
            password_hash="not-used",
            role="test",
            is_active=True,
        )

    def override_get_db() -> Generator[FakeSession, None, None]:
        yield FakeSession()

    def override_get_service() -> FakeNotificationsService:
        return service

    monkeypatch.setattr(
        notification_routes,
        "get_notifications_service",
        lambda db=None: service,
    )
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[original_get_service] = override_get_service

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides = original_overrides


def assert_notification_contract(notification: dict[str, object]) -> None:
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


def assert_delivery_contract(delivery: dict[str, object]) -> None:
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


def test_notifications_routes_are_registered(client: TestClient) -> None:
    route_paths = {getattr(route, "path", "") for route in app.routes}

    assert BASE_URL in route_paths
    assert f"{BASE_URL}/health" in route_paths
    assert f"{BASE_URL}/{{notification_id}}" in route_paths
    assert f"{BASE_URL}/uuid/{{notification_uuid}}" in route_paths
    assert f"{BASE_URL}/deliveries" in route_paths
    assert f"{BASE_URL}/deliveries/{{delivery_id}}" in route_paths
    assert f"{BASE_URL}/deliveries/uuid/{{delivery_uuid}}" in route_paths


def test_notifications_openapi_contains_expected_paths(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert BASE_URL in paths
    assert "get" in paths[BASE_URL]
    assert "post" in paths[BASE_URL]
    assert f"{BASE_URL}/health" in paths
    assert f"{BASE_URL}/{{notification_id}}" in paths
    assert f"{BASE_URL}/uuid/{{notification_uuid}}" in paths
    assert f"{BASE_URL}/deliveries" in paths
    assert "get" in paths[f"{BASE_URL}/deliveries"]
    assert "post" in paths[f"{BASE_URL}/deliveries"]
    assert f"{BASE_URL}/deliveries/{{delivery_id}}" in paths
    assert f"{BASE_URL}/deliveries/uuid/{{delivery_uuid}}" in paths


def test_notifications_health_contract(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_notification_list_exposes_response_and_query_contract(
    client: TestClient,
    service: FakeNotificationsService,
) -> None:
    response = client.get(
        BASE_URL,
        params={
            "recipient_user_id": 1,
            "actor_user_id": 1,
            "type": "system",
            "channel": "in_app",
            "priority": "normal",
            "status": "pending",
            "entity_type": "document",
            "entity_id": "DOC-001",
            "correlation_id": "corr-001",
            "request_id": "req-001",
            "created_from": "2026-07-05T00:00:00Z",
            "created_to": "2026-07-06T00:00:00Z",
            "include_deleted": False,
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
    assert_notification_contract(body["items"][0])
    assert service.last_notification_list_filters is not None
    assert service.last_notification_list_filters["limit"] == 25
    assert service.last_notification_list_filters["offset"] == 5
    assert service.last_notification_list_filters["channel"] == "in_app"
    assert service.last_notification_count_filters is not None
    assert "limit" not in service.last_notification_count_filters
    assert "offset" not in service.last_notification_count_filters


def test_notification_create_and_get_contract(client: TestClient) -> None:
    create_response = client.post(
        BASE_URL,
        json={
            "recipient_user_id": 1,
            "actor_user_id": None,
            "type": "workflow",
            "channel": "email",
            "priority": "high",
            "status": "pending",
            "title": "Procedure approval requested",
            "body": "Please approve the updated procedure.",
            "payload": {"document_number": "DOC-002"},
            "entity_type": "document",
            "entity_id": "DOC-002",
            "correlation_id": "corr-002",
            "request_id": "req-002",
        },
    )
    detail_response = client.get(f"{BASE_URL}/2")

    assert create_response.status_code == 201
    created_notification = create_response.json()
    assert_notification_contract(created_notification)
    assert created_notification["title"] == "Procedure approval requested"
    assert created_notification["payload"] == {"document_number": "DOC-002"}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == 2


def test_notification_uuid_detail_contract(client: TestClient) -> None:
    response = client.get(
        f"{BASE_URL}/uuid/11111111-1111-4111-8111-111111111111",
    )

    assert response.status_code == 200
    assert response.json()["notification_uuid"] == (
        "11111111-1111-4111-8111-111111111111"
    )


def test_notification_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    missing_get_response = client.get(f"{BASE_URL}/999")
    missing_uuid_response = client.get(
        f"{BASE_URL}/uuid/33333333-3333-4333-8333-333333333333",
    )
    create_validation_response = client.post(
        BASE_URL,
        json={"body": "Missing required title"},
    )
    query_validation_response = client.get(f"{BASE_URL}?limit=0")

    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {"detail": "Notification not found"}
    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {"detail": "Notification not found"}
    assert create_validation_response.status_code == 422
    assert query_validation_response.status_code == 422


def test_delivery_list_exposes_response_and_query_contract(
    client: TestClient,
    service: FakeNotificationsService,
) -> None:
    response = client.get(
        f"{BASE_URL}/deliveries",
        params={
            "notification_id": 1,
            "channel": "in_app",
            "provider": "internal",
            "provider_message_id": "msg-001",
            "status": "pending",
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
    assert_delivery_contract(body["items"][0])
    assert service.last_delivery_list_filters is not None
    assert service.last_delivery_list_filters["limit"] == 25
    assert service.last_delivery_list_filters["offset"] == 5
    assert service.last_delivery_list_filters["provider"] == "internal"
    assert service.last_delivery_count_filters is not None
    assert "limit" not in service.last_delivery_count_filters
    assert "offset" not in service.last_delivery_count_filters


def test_delivery_create_and_get_contract(client: TestClient) -> None:
    create_response = client.post(
        f"{BASE_URL}/deliveries",
        json={
            "notification_id": 1,
            "channel": "email",
            "provider": "smtp",
            "provider_message_id": "msg-002",
            "status": "sent",
            "attempt_count": 1,
            "provider_response": {"message_id": "msg-002"},
        },
    )
    detail_response = client.get(f"{BASE_URL}/deliveries/2")

    assert create_response.status_code == 201
    created_delivery = create_response.json()
    assert_delivery_contract(created_delivery)
    assert created_delivery["provider"] == "smtp"
    assert created_delivery["provider_response"] == {"message_id": "msg-002"}
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == 2


def test_delivery_uuid_detail_contract(client: TestClient) -> None:
    response = client.get(
        f"{BASE_URL}/deliveries/uuid/22222222-2222-4222-8222-222222222222",
    )

    assert response.status_code == 200
    assert response.json()["delivery_uuid"] == (
        "22222222-2222-4222-8222-222222222222"
    )


def test_delivery_endpoints_return_not_found_and_validation_errors(
    client: TestClient,
) -> None:
    missing_get_response = client.get(f"{BASE_URL}/deliveries/999")
    missing_uuid_response = client.get(
        f"{BASE_URL}/deliveries/uuid/44444444-4444-4444-8444-444444444444",
    )
    create_validation_response = client.post(
        f"{BASE_URL}/deliveries",
        json={"status": "pending"},
    )
    query_validation_response = client.get(f"{BASE_URL}/deliveries?limit=0")

    assert missing_get_response.status_code == 404
    assert missing_get_response.json() == {
        "detail": "Notification delivery not found",
    }
    assert missing_uuid_response.status_code == 404
    assert missing_uuid_response.json() == {
        "detail": "Notification delivery not found",
    }
    assert create_validation_response.status_code == 422
    assert query_validation_response.status_code == 422
