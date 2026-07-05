from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

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
from app.modules.notifications.repository import (
    NotificationDeliveryRepository,
    NotificationRepository,
    NotificationsRepository,
)
from app.modules.notifications.service import NotificationsService


@pytest.fixture()
def service(db_session: Session) -> NotificationsService:
    return NotificationsService(NotificationsRepository(db_session))


def create_test_user(
    db_session: Session,
    username: str = "notifications-service-user",
) -> User:
    user = User(
        username=username,
        full_name="Notifications Service User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_notification(
    service: NotificationsService,
    *,
    recipient_user_id: int | None = None,
    actor_user_id: int | None = None,
    type: str = NotificationType.SYSTEM.value,
    channel: str = NotificationChannel.IN_APP.value,
    priority: str = NotificationPriority.NORMAL.value,
    status: str = NotificationStatus.PENDING.value,
    title: str = "Service notification",
    body: str | None = "Service notification body",
    payload: dict[str, object] | None = None,
    entity_type: str | None = "document",
    entity_id: str | None = "DOC-SVC-001",
    correlation_id: str | None = "correlation-svc-001",
    request_id: str | None = "request-svc-001",
    scheduled_at: datetime | None = None,
    sent_at: datetime | None = None,
    created_at: datetime | None = None,
) -> Notification:
    return service.create_notification(
        Notification(
            recipient_user_id=recipient_user_id,
            actor_user_id=actor_user_id,
            type=type,
            channel=channel,
            priority=priority,
            status=status,
            title=title,
            body=body,
            payload=payload
            if payload is not None
            else {"source": "service-test", "tags": ["notifications"]},
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            request_id=request_id,
            scheduled_at=scheduled_at,
            sent_at=sent_at,
            created_at=created_at,
        ),
    )


def create_delivery(
    service: NotificationsService,
    *,
    notification_id: int,
    channel: str = NotificationChannel.IN_APP.value,
    provider: str | None = NotificationProvider.INTERNAL.value,
    provider_message_id: str | None = "message-svc-001",
    status: str = NotificationDeliveryStatus.PENDING.value,
    attempt_count: int = 0,
    last_attempt_at: datetime | None = None,
    delivered_at: datetime | None = None,
    failed_at: datetime | None = None,
    failure_reason: str | None = None,
    provider_response: dict[str, object] | None = None,
    created_at: datetime | None = None,
) -> NotificationDelivery:
    return service.create_delivery(
        NotificationDelivery(
            notification_id=notification_id,
            channel=channel,
            provider=provider,
            provider_message_id=provider_message_id,
            status=status,
            attempt_count=attempt_count,
            last_attempt_at=last_attempt_at,
            delivered_at=delivered_at,
            failed_at=failed_at,
            failure_reason=failure_reason,
            provider_response=provider_response
            if provider_response is not None
            else {"source": "service-test"},
            created_at=created_at,
        ),
    )


def test_notifications_service_create_lookup_aliases_and_missing_behavior(
    service: NotificationsService,
    db_session: Session,
) -> None:
    recipient = create_test_user(db_session)
    actor = create_test_user(db_session, "notifications-service-actor")

    notification = create_notification(
        service,
        recipient_user_id=recipient.id,
        actor_user_id=actor.id,
    )
    alias_notification = service.create(
        Notification(
            recipient_user_id=recipient.id,
            type=NotificationType.REMINDER.value,
            channel=NotificationChannel.EMAIL.value,
            priority=NotificationPriority.HIGH.value,
            status=NotificationStatus.SCHEDULED.value,
            title="Alias service notification",
            entity_type="task",
            entity_id="TASK-SVC-001",
        ),
    )

    assert service.health() == {"status": "ok"}
    assert notification.id is not None
    assert notification.notification_uuid is not None
    assert alias_notification.id is not None
    assert db_session.get(Notification, notification.id) == notification
    assert service.get_notification(notification.id) == notification
    assert service.get_by_id(notification.id) == notification
    assert service.get_notification_by_uuid(notification.notification_uuid) == notification
    assert service.get_by_uuid(notification.notification_uuid) == notification
    assert service.notification_exists(notification.id) is True
    assert service.exists(notification.id) is True
    assert notification.payload == {
        "source": "service-test",
        "tags": ["notifications"],
    }

    assert service.get_notification(999) is None
    assert service.get_by_id(999) is None
    assert service.get_notification_by_uuid(uuid4()) is None
    assert service.get_by_uuid(uuid4()) is None
    assert service.notification_exists(999) is False
    assert service.exists(999) is False


def test_notifications_service_list_filters_count_ordering_and_pagination(
    service: NotificationsService,
    db_session: Session,
) -> None:
    recipient = create_test_user(db_session, "notifications-service-filter-recipient")
    other_recipient = create_test_user(db_session, "notifications-service-filter-other")
    actor = create_test_user(db_session, "notifications-service-filter-actor")

    first_notification = create_notification(
        service,
        recipient_user_id=recipient.id,
        actor_user_id=actor.id,
        type=NotificationType.SYSTEM.value,
        channel=NotificationChannel.IN_APP.value,
        priority=NotificationPriority.NORMAL.value,
        status=NotificationStatus.PENDING.value,
        title="First service notification",
        entity_type="document",
        entity_id="DOC-SVC-001",
        correlation_id="correlation-service-docs",
        request_id="request-service-001",
        scheduled_at=datetime(2026, 7, 5, 8, 30, 0),
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second_notification = create_notification(
        service,
        recipient_user_id=recipient.id,
        actor_user_id=actor.id,
        type=NotificationType.REMINDER.value,
        channel=NotificationChannel.EMAIL.value,
        priority=NotificationPriority.HIGH.value,
        status=NotificationStatus.SENT.value,
        title="Second service notification",
        entity_type="task",
        entity_id="TASK-SVC-001",
        correlation_id="correlation-service-tasks",
        request_id="request-service-002",
        scheduled_at=datetime(2026, 7, 5, 9, 30, 0),
        sent_at=datetime(2026, 7, 5, 10, 5, 0),
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third_notification = create_notification(
        service,
        recipient_user_id=other_recipient.id,
        type=NotificationType.ALERT.value,
        channel=NotificationChannel.PUSH.value,
        priority=NotificationPriority.URGENT.value,
        status=NotificationStatus.FAILED.value,
        title="Third service notification",
        entity_type="incident",
        entity_id="INC-SVC-001",
        correlation_id="correlation-service-alerts",
        request_id="request-service-003",
        scheduled_at=datetime(2026, 7, 5, 10, 30, 0),
        sent_at=datetime(2026, 7, 5, 11, 5, 0),
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert service.list_notifications() == [
        third_notification,
        second_notification,
        first_notification,
    ]
    assert service.list() == [third_notification, second_notification, first_notification]
    assert service.list_notifications(limit=2) == [
        third_notification,
        second_notification,
    ]
    assert service.list_notifications(offset=1, limit=1) == [second_notification]

    assert service.list_notifications(recipient_user_id=recipient.id) == [
        second_notification,
        first_notification,
    ]
    assert service.list_notifications(actor_user_id=actor.id) == [
        second_notification,
        first_notification,
    ]
    assert service.list_notifications(type=NotificationType.REMINDER.value) == [
        second_notification
    ]
    assert service.list_notifications(channel=NotificationChannel.PUSH.value) == [
        third_notification
    ]
    assert service.list_notifications(priority=NotificationPriority.NORMAL.value) == [
        first_notification
    ]
    assert service.list_notifications(status=NotificationStatus.FAILED.value) == [
        third_notification
    ]
    assert service.list_notifications(entity_type="document") == [first_notification]
    assert service.list_notifications(entity_id="TASK-SVC-001") == [second_notification]
    assert service.list_notifications(correlation_id="correlation-service-docs") == [
        first_notification
    ]
    assert service.list_notifications(request_id="request-service-003") == [
        third_notification
    ]
    assert service.list_notifications(
        scheduled_from=datetime(2026, 7, 5, 9, 0, 0),
    ) == [third_notification, second_notification]
    assert service.list_notifications(
        scheduled_to=datetime(2026, 7, 5, 9, 30, 0),
    ) == [second_notification, first_notification]
    assert service.list_notifications(sent_from=datetime(2026, 7, 5, 11, 0, 0)) == [
        third_notification
    ]
    assert service.list_notifications(sent_to=datetime(2026, 7, 5, 10, 30, 0)) == [
        second_notification
    ]
    assert service.list_notifications(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        third_notification,
        second_notification,
    ]
    assert service.list_notifications(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [
        second_notification,
        first_notification,
    ]
    assert service.list_notifications(entity_type="missing") == []

    assert service.count_notifications() == 3
    assert service.count() == 3
    assert service.count_notifications(recipient_user_id=recipient.id) == 2
    assert service.count_notifications(type=NotificationType.ALERT.value) == 1
    assert service.count_notifications(channel=NotificationChannel.EMAIL.value) == 1
    assert service.count_notifications(priority=NotificationPriority.HIGH.value) == 1
    assert service.count_notifications(status=NotificationStatus.PENDING.value) == 1
    assert service.count_notifications(
        entity_type="task",
        entity_id="TASK-SVC-001",
    ) == 1
    assert service.count_notifications(correlation_id="missing") == 0


def test_notifications_service_update_uuid_stability_and_soft_delete_lifecycle(
    service: NotificationsService,
) -> None:
    active_notification = create_notification(
        service,
        title="Active service notification",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )
    deleted_notification = create_notification(
        service,
        title="Deleted service notification",
        created_at=datetime(2026, 7, 5, 12, 0, 0),
    )
    original_uuid = active_notification.notification_uuid

    updated_notification = service.update_notification(
        active_notification.id,
        {
            "status": NotificationStatus.READ.value,
            "priority": NotificationPriority.URGENT.value,
            "title": "Updated service notification",
            "body": "Updated service body",
            "payload": {"source": "updated-service", "version": 2},
            "entity_type": "case",
            "entity_id": "CASE-SVC-001",
            "read_at": datetime(2026, 7, 5, 12, 0, 0),
        },
    )

    assert updated_notification is active_notification
    assert service.update(
        active_notification.id,
        {"status": NotificationStatus.SENT.value},
    ) is active_notification
    assert active_notification.notification_uuid == original_uuid
    assert service.get_notification_by_uuid(original_uuid) == active_notification
    assert active_notification.status == NotificationStatus.SENT.value
    assert active_notification.priority == NotificationPriority.URGENT.value
    assert active_notification.title == "Updated service notification"
    assert active_notification.body == "Updated service body"
    assert active_notification.payload == {"source": "updated-service", "version": 2}
    assert active_notification.entity_type == "case"
    assert active_notification.entity_id == "CASE-SVC-001"
    assert active_notification.read_at == datetime(2026, 7, 5, 12, 0, 0)

    assert service.update_notification(
        999,
        {"status": NotificationStatus.FAILED.value},
    ) is None
    with pytest.raises(
        ValueError,
        match="Unsupported notification update fields: id",
    ):
        service.update_notification(active_notification.id, {"id": 999})

    assert service.mark_notification_deleted(deleted_notification.id) is True
    assert deleted_notification.deleted_at is not None
    assert service.get_notification(deleted_notification.id) is None
    assert service.get_by_id(deleted_notification.id) is None
    assert service.get_notification(
        deleted_notification.id,
        include_deleted=True,
    ) == deleted_notification
    assert service.get_notification_by_uuid(deleted_notification.notification_uuid) is None
    assert service.get_notification_by_uuid(
        deleted_notification.notification_uuid,
        include_deleted=True,
    ) == deleted_notification
    assert service.notification_exists(deleted_notification.id) is False
    assert service.exists(deleted_notification.id, include_deleted=True) is True
    assert service.list_notifications() == [active_notification]
    assert service.count_notifications() == 1
    assert service.list_notifications(include_deleted=True) == [
        deleted_notification,
        active_notification,
    ]
    assert service.count_notifications(include_deleted=True) == 2

    assert service.delete_notification(999) is False
    assert service.delete(999) is False
    assert service.mark_deleted(999) is False


def test_notifications_service_delivery_create_lookup_and_missing_behavior(
    service: NotificationsService,
    db_session: Session,
) -> None:
    recipient = create_test_user(db_session, "notifications-service-delivery-user")
    notification = create_notification(service, recipient_user_id=recipient.id)

    delivery = create_delivery(
        service,
        notification_id=notification.id,
        channel=NotificationChannel.IN_APP.value,
        provider=NotificationProvider.INTERNAL.value,
    )
    alias_delivery = service.create_notification_delivery(
        NotificationDelivery(
            notification_id=notification.id,
            channel=NotificationChannel.EMAIL.value,
            provider=NotificationProvider.SMTP.value,
            provider_message_id="message-service-alias",
            status=NotificationDeliveryStatus.SENT.value,
            attempt_count=1,
        ),
    )

    assert delivery.id is not None
    assert delivery.delivery_uuid is not None
    assert alias_delivery.id is not None
    assert db_session.get(NotificationDelivery, delivery.id) == delivery
    assert service.get_delivery(delivery.id) == delivery
    assert service.get_delivery_by_id(delivery.id) == delivery
    assert service.get_delivery_by_uuid(delivery.delivery_uuid) == delivery
    assert service.delivery_exists(delivery.id) is True
    assert delivery.provider_response == {"source": "service-test"}

    assert service.get_delivery(999) is None
    assert service.get_delivery_by_id(999) is None
    assert service.get_delivery_by_uuid(uuid4()) is None
    assert service.delivery_exists(999) is False


def test_notifications_service_delivery_filters_count_update_and_status_lifecycle(
    service: NotificationsService,
    db_session: Session,
) -> None:
    recipient = create_test_user(db_session, "notifications-service-delivery-filter")
    notification = create_notification(service, recipient_user_id=recipient.id)
    other_notification = create_notification(
        service,
        recipient_user_id=recipient.id,
        title="Other service notification",
        created_at=datetime(2026, 7, 5, 12, 0, 0),
    )

    first_delivery = create_delivery(
        service,
        notification_id=notification.id,
        channel=NotificationChannel.IN_APP.value,
        provider=NotificationProvider.INTERNAL.value,
        provider_message_id="message-service-001",
        status=NotificationDeliveryStatus.PENDING.value,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second_delivery = create_delivery(
        service,
        notification_id=notification.id,
        channel=NotificationChannel.EMAIL.value,
        provider=NotificationProvider.SMTP.value,
        provider_message_id="message-service-002",
        status=NotificationDeliveryStatus.SENT.value,
        attempt_count=1,
        last_attempt_at=datetime(2026, 7, 5, 10, 5, 0),
        provider_response={"provider": "smtp"},
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third_delivery = create_delivery(
        service,
        notification_id=other_notification.id,
        channel=NotificationChannel.WEBHOOK.value,
        provider=NotificationProvider.WEBHOOK.value,
        provider_message_id="message-service-003",
        status=NotificationDeliveryStatus.FAILED.value,
        attempt_count=2,
        last_attempt_at=datetime(2026, 7, 5, 11, 5, 0),
        failed_at=datetime(2026, 7, 5, 11, 10, 0),
        failure_reason="timeout",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )
    original_uuid = first_delivery.delivery_uuid

    assert service.list_deliveries() == [third_delivery, second_delivery, first_delivery]
    assert service.list_deliveries(limit=2) == [third_delivery, second_delivery]
    assert service.list_deliveries(offset=1, limit=1) == [second_delivery]
    assert service.list_deliveries(notification_id=notification.id) == [
        second_delivery,
        first_delivery,
    ]
    assert service.list_deliveries(channel=NotificationChannel.EMAIL.value) == [
        second_delivery
    ]
    assert service.list_deliveries(provider=NotificationProvider.WEBHOOK.value) == [
        third_delivery
    ]
    assert service.list_deliveries(provider_message_id="message-service-001") == [
        first_delivery
    ]
    assert service.list_deliveries(status=NotificationDeliveryStatus.FAILED.value) == [
        third_delivery
    ]
    assert service.list_deliveries(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        third_delivery,
        second_delivery,
    ]
    assert service.list_deliveries(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [
        second_delivery,
        first_delivery,
    ]
    assert service.list_deliveries(
        last_attempt_from=datetime(2026, 7, 5, 11, 0, 0),
    ) == [third_delivery]
    assert service.list_deliveries(
        last_attempt_to=datetime(2026, 7, 5, 10, 30, 0),
    ) == [second_delivery]
    assert service.list_deliveries(failed_from=datetime(2026, 7, 5, 11, 0, 0)) == [
        third_delivery
    ]
    assert service.list_deliveries(failed_to=datetime(2026, 7, 5, 11, 30, 0)) == [
        third_delivery
    ]
    assert service.list_deliveries(provider="missing") == []

    assert service.count_deliveries() == 3
    assert service.count_deliveries(notification_id=notification.id) == 2
    assert service.count_deliveries(channel=NotificationChannel.IN_APP.value) == 1
    assert service.count_deliveries(provider=NotificationProvider.SMTP.value) == 1
    assert service.count_deliveries(status=NotificationDeliveryStatus.PENDING.value) == 1
    assert service.count_deliveries(provider_message_id="missing") == 0

    updated_delivery = service.update_delivery(
        first_delivery.id,
        {
            "channel": NotificationChannel.EMAIL.value,
            "provider": NotificationProvider.SMTP.value,
            "provider_message_id": "message-service-updated",
            "status": NotificationDeliveryStatus.SENT.value,
            "attempt_count": 1,
            "last_attempt_at": datetime(2026, 7, 5, 12, 10, 0),
            "provider_response": {"accepted": True},
        },
    )

    assert updated_delivery is first_delivery
    assert first_delivery.delivery_uuid == original_uuid
    assert service.get_delivery_by_uuid(original_uuid) == first_delivery
    assert first_delivery.channel == NotificationChannel.EMAIL.value
    assert first_delivery.provider == NotificationProvider.SMTP.value
    assert first_delivery.provider_message_id == "message-service-updated"
    assert first_delivery.attempt_count == 1
    assert first_delivery.provider_response == {"accepted": True}

    delivered_at = datetime(2026, 7, 5, 12, 15, 0)
    marked_delivery = service.update_delivery_status(
        first_delivery.id,
        NotificationDeliveryStatus.DELIVERED.value,
        last_attempt_at=datetime(2026, 7, 5, 12, 20, 0),
        delivered_at=delivered_at,
        provider_message_id="message-service-delivered",
        provider_response={"delivered": True},
    )
    alias_marked_delivery = service.mark_delivery_status(
        first_delivery.id,
        NotificationDeliveryStatus.FAILED.value,
        failed_at=datetime(2026, 7, 5, 12, 30, 0),
        failure_reason="downstream rejected",
        provider_response={"delivered": False},
    )

    assert marked_delivery is first_delivery
    assert alias_marked_delivery is first_delivery
    assert first_delivery.status == NotificationDeliveryStatus.FAILED.value
    assert first_delivery.delivered_at == delivered_at
    assert first_delivery.failed_at == datetime(2026, 7, 5, 12, 30, 0)
    assert first_delivery.failure_reason == "downstream rejected"
    assert first_delivery.provider_message_id == "message-service-delivered"
    assert first_delivery.provider_response == {"delivered": False}

    assert service.update_delivery(
        999,
        {"status": NotificationDeliveryStatus.FAILED.value},
    ) is None
    assert service.update_delivery_status(
        999,
        NotificationDeliveryStatus.FAILED.value,
    ) is None
    assert service.mark_delivery_status(
        999,
        NotificationDeliveryStatus.FAILED.value,
    ) is None
    with pytest.raises(
        ValueError,
        match="Unsupported notification delivery update fields: notification_id",
    ):
        service.update_delivery(first_delivery.id, {"notification_id": other_notification.id})


def test_notifications_service_aggregate_repository_and_lifecycle_consistency(
    service: NotificationsService,
    db_session: Session,
) -> None:
    recipient = create_test_user(db_session, "notifications-service-aggregate")
    notification = create_notification(service, recipient_user_id=recipient.id)
    delivery = create_delivery(
        service,
        notification_id=notification.id,
        channel=NotificationChannel.EMAIL.value,
        provider=NotificationProvider.SMTP.value,
    )

    assert service.repository.db is db_session
    assert isinstance(service.repository.notifications, NotificationRepository)
    assert isinstance(service.repository.deliveries, NotificationDeliveryRepository)
    assert service.repository.health() is True
    assert service.health() == {"status": "ok"}
    assert service.get_notification(notification.id) == notification
    assert service.get_delivery(delivery.id) == delivery
    assert delivery.notification_id == notification.id
    assert delivery.delivery_uuid != notification.notification_uuid

    assert service.delete_notification(notification.id) is True
    assert service.get_notification(notification.id) is None
    assert service.get_notification(
        notification.id,
        include_deleted=True,
    ) == notification
    assert service.get_delivery(delivery.id) == delivery
    assert service.list_deliveries(notification_id=notification.id) == [delivery]
