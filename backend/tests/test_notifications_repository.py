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


def create_test_user(
    db_session: Session,
    username: str = "notifications-repository-user",
) -> User:
    user = User(
        username=username,
        full_name="Notifications Repository User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_notification(
    repository: NotificationRepository,
    *,
    recipient_user_id: int | None = None,
    actor_user_id: int | None = None,
    type: str = NotificationType.SYSTEM.value,
    channel: str = NotificationChannel.IN_APP.value,
    priority: str = NotificationPriority.NORMAL.value,
    status: str = NotificationStatus.PENDING.value,
    title: str = "Repository notification",
    body: str | None = "Repository notification body",
    payload: dict[str, object] | None = None,
    entity_type: str | None = "document",
    entity_id: str | None = "DOC-001",
    correlation_id: str | None = "correlation-001",
    request_id: str | None = "request-001",
    scheduled_at: datetime | None = None,
    sent_at: datetime | None = None,
    created_at: datetime | None = None,
) -> Notification:
    return repository.create(
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
            else {"source": "repository-test", "tags": ["notifications"]},
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
    repository: NotificationDeliveryRepository,
    *,
    notification_id: int,
    channel: str = NotificationChannel.IN_APP.value,
    provider: str | None = NotificationProvider.INTERNAL.value,
    provider_message_id: str | None = "message-001",
    status: str = NotificationDeliveryStatus.PENDING.value,
    attempt_count: int = 0,
    last_attempt_at: datetime | None = None,
    delivered_at: datetime | None = None,
    failed_at: datetime | None = None,
    failure_reason: str | None = None,
    provider_response: dict[str, object] | None = None,
    created_at: datetime | None = None,
) -> NotificationDelivery:
    return repository.create(
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
            else {"source": "repository-test"},
            created_at=created_at,
        ),
    )


def test_notification_create_lookup_update_soft_delete_and_health(
    db_session: Session,
) -> None:
    repository = NotificationRepository(db_session)
    recipient = create_test_user(db_session)
    actor = create_test_user(db_session, "notifications-repository-actor")

    notification = create_notification(
        repository,
        recipient_user_id=recipient.id,
        actor_user_id=actor.id,
    )
    alias_notification = repository.create_notification(
        Notification(
            recipient_user_id=recipient.id,
            type=NotificationType.REMINDER.value,
            channel=NotificationChannel.EMAIL.value,
            priority=NotificationPriority.HIGH.value,
            status=NotificationStatus.SCHEDULED.value,
            title="Alias notification",
            entity_type="task",
            entity_id="TASK-001",
        ),
    )
    original_uuid = notification.notification_uuid

    assert repository.health() is True
    assert notification.id is not None
    assert notification.notification_uuid is not None
    assert alias_notification.id is not None
    assert db_session.get(Notification, notification.id) == notification
    assert repository.get_by_id(notification.id) == notification
    assert repository.get_by_uuid(notification.notification_uuid) == notification
    assert repository.exists(notification.id) is True
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert repository.exists(999) is False
    assert notification.payload == {
        "source": "repository-test",
        "tags": ["notifications"],
    }

    updated_notification = repository.update(
        notification.id,
        {
            "status": NotificationStatus.READ.value,
            "priority": NotificationPriority.URGENT.value,
            "title": "Updated notification",
            "body": "Updated body",
            "payload": {"source": "updated", "version": 2},
            "entity_type": "case",
            "entity_id": "CASE-001",
            "read_at": datetime(2026, 7, 5, 12, 0, 0),
        },
    )

    assert updated_notification is notification
    assert notification.notification_uuid == original_uuid
    assert repository.get_by_uuid(original_uuid) == notification
    assert notification.status == NotificationStatus.READ.value
    assert notification.priority == NotificationPriority.URGENT.value
    assert notification.title == "Updated notification"
    assert notification.body == "Updated body"
    assert notification.payload == {"source": "updated", "version": 2}
    assert notification.entity_type == "case"
    assert notification.entity_id == "CASE-001"
    assert notification.read_at == datetime(2026, 7, 5, 12, 0, 0)

    assert repository.update(999, {"status": NotificationStatus.FAILED.value}) is None
    with pytest.raises(
        ValueError,
        match="Unsupported notification update fields: id",
    ):
        repository.update(notification.id, {"id": 999})

    assert repository.mark_deleted(notification.id) is True
    assert notification.deleted_at is not None
    assert repository.get_by_id(notification.id) is None
    assert repository.get_by_id(notification.id, include_deleted=True) == notification
    assert repository.get_by_uuid(original_uuid) is None
    assert repository.get_by_uuid(original_uuid, include_deleted=True) == notification
    assert repository.exists(notification.id) is False
    assert repository.exists(notification.id, include_deleted=True) is True
    assert repository.list() == [alias_notification]
    assert repository.count() == 1
    assert repository.list(include_deleted=True) == [alias_notification, notification]
    assert repository.count(include_deleted=True) == 2
    assert repository.delete(999) is False
    assert repository.mark_deleted(999) is False


def test_notification_list_filters_count_ordering_and_pagination(
    db_session: Session,
) -> None:
    repository = NotificationRepository(db_session)
    recipient = create_test_user(db_session, "notifications-filter-recipient")
    other_recipient = create_test_user(db_session, "notifications-filter-other")
    actor = create_test_user(db_session, "notifications-filter-actor")

    first_notification = create_notification(
        repository,
        recipient_user_id=recipient.id,
        actor_user_id=actor.id,
        type=NotificationType.SYSTEM.value,
        channel=NotificationChannel.IN_APP.value,
        priority=NotificationPriority.NORMAL.value,
        status=NotificationStatus.PENDING.value,
        title="First notification",
        entity_type="document",
        entity_id="DOC-001",
        correlation_id="correlation-docs",
        request_id="request-001",
        scheduled_at=datetime(2026, 7, 5, 8, 30, 0),
        sent_at=None,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second_notification = create_notification(
        repository,
        recipient_user_id=recipient.id,
        actor_user_id=actor.id,
        type=NotificationType.REMINDER.value,
        channel=NotificationChannel.EMAIL.value,
        priority=NotificationPriority.HIGH.value,
        status=NotificationStatus.SENT.value,
        title="Second notification",
        entity_type="task",
        entity_id="TASK-001",
        correlation_id="correlation-tasks",
        request_id="request-002",
        scheduled_at=datetime(2026, 7, 5, 9, 30, 0),
        sent_at=datetime(2026, 7, 5, 10, 5, 0),
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third_notification = create_notification(
        repository,
        recipient_user_id=other_recipient.id,
        actor_user_id=None,
        type=NotificationType.ALERT.value,
        channel=NotificationChannel.PUSH.value,
        priority=NotificationPriority.URGENT.value,
        status=NotificationStatus.FAILED.value,
        title="Third notification",
        entity_type="incident",
        entity_id="INC-001",
        correlation_id="correlation-alerts",
        request_id="request-003",
        scheduled_at=datetime(2026, 7, 5, 10, 30, 0),
        sent_at=datetime(2026, 7, 5, 11, 5, 0),
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert repository.list() == [
        third_notification,
        second_notification,
        first_notification,
    ]
    assert repository.list(limit=2) == [third_notification, second_notification]
    assert repository.list(offset=1, limit=1) == [second_notification]

    assert repository.list(recipient_user_id=recipient.id) == [
        second_notification,
        first_notification,
    ]
    assert repository.list(actor_user_id=actor.id) == [
        second_notification,
        first_notification,
    ]
    assert repository.list(type=NotificationType.REMINDER.value) == [
        second_notification
    ]
    assert repository.list(channel=NotificationChannel.PUSH.value) == [
        third_notification
    ]
    assert repository.list(priority=NotificationPriority.NORMAL.value) == [
        first_notification
    ]
    assert repository.list(status=NotificationStatus.FAILED.value) == [
        third_notification
    ]
    assert repository.list(entity_type="document") == [first_notification]
    assert repository.list(entity_id="TASK-001") == [second_notification]
    assert repository.list(correlation_id="correlation-docs") == [
        first_notification
    ]
    assert repository.list(request_id="request-003") == [third_notification]
    assert repository.list(
        scheduled_from=datetime(2026, 7, 5, 9, 0, 0),
    ) == [third_notification, second_notification]
    assert repository.list(
        scheduled_to=datetime(2026, 7, 5, 9, 30, 0),
    ) == [second_notification, first_notification]
    assert repository.list(sent_from=datetime(2026, 7, 5, 11, 0, 0)) == [
        third_notification
    ]
    assert repository.list(sent_to=datetime(2026, 7, 5, 10, 30, 0)) == [
        second_notification
    ]
    assert repository.list(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        third_notification,
        second_notification,
    ]
    assert repository.list(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [
        second_notification,
        first_notification,
    ]
    assert repository.list(entity_type="missing") == []

    assert repository.count() == 3
    assert repository.count(recipient_user_id=recipient.id) == 2
    assert repository.count(type=NotificationType.ALERT.value) == 1
    assert repository.count(channel=NotificationChannel.EMAIL.value) == 1
    assert repository.count(priority=NotificationPriority.HIGH.value) == 1
    assert repository.count(status=NotificationStatus.PENDING.value) == 1
    assert repository.count(entity_type="task", entity_id="TASK-001") == 1
    assert repository.count(correlation_id="missing") == 0


def test_delivery_create_lookup_update_mark_status_filters_and_health(
    db_session: Session,
) -> None:
    notification_repository = NotificationRepository(db_session)
    delivery_repository = NotificationDeliveryRepository(db_session)
    recipient = create_test_user(db_session, "notifications-delivery-recipient")
    notification = create_notification(
        notification_repository,
        recipient_user_id=recipient.id,
    )
    other_notification = create_notification(
        notification_repository,
        recipient_user_id=recipient.id,
        title="Other notification",
        created_at=datetime(2026, 7, 5, 12, 0, 0),
    )

    first_delivery = create_delivery(
        delivery_repository,
        notification_id=notification.id,
        channel=NotificationChannel.IN_APP.value,
        provider=NotificationProvider.INTERNAL.value,
        provider_message_id="message-001",
        status=NotificationDeliveryStatus.PENDING.value,
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second_delivery = delivery_repository.create_delivery(
        NotificationDelivery(
            notification_id=notification.id,
            channel=NotificationChannel.EMAIL.value,
            provider=NotificationProvider.SMTP.value,
            provider_message_id="message-002",
            status=NotificationDeliveryStatus.SENT.value,
            attempt_count=1,
            last_attempt_at=datetime(2026, 7, 5, 10, 5, 0),
            provider_response={"provider": "smtp"},
            created_at=datetime(2026, 7, 5, 10, 0, 0),
        ),
    )
    third_delivery = create_delivery(
        delivery_repository,
        notification_id=other_notification.id,
        channel=NotificationChannel.WEBHOOK.value,
        provider=NotificationProvider.WEBHOOK.value,
        provider_message_id="message-003",
        status=NotificationDeliveryStatus.FAILED.value,
        attempt_count=2,
        last_attempt_at=datetime(2026, 7, 5, 11, 5, 0),
        failed_at=datetime(2026, 7, 5, 11, 10, 0),
        failure_reason="timeout",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )
    original_uuid = first_delivery.delivery_uuid

    assert delivery_repository.health() is True
    assert first_delivery.id is not None
    assert first_delivery.delivery_uuid is not None
    assert db_session.get(NotificationDelivery, first_delivery.id) == first_delivery
    assert delivery_repository.get_by_id(first_delivery.id) == first_delivery
    assert delivery_repository.get_by_uuid(first_delivery.delivery_uuid) == first_delivery
    assert delivery_repository.exists(first_delivery.id) is True
    assert delivery_repository.get_by_id(999) is None
    assert delivery_repository.get_by_uuid(uuid4()) is None
    assert delivery_repository.exists(999) is False
    assert first_delivery.provider_response == {"source": "repository-test"}

    assert delivery_repository.list() == [
        third_delivery,
        second_delivery,
        first_delivery,
    ]
    assert delivery_repository.list(limit=2) == [third_delivery, second_delivery]
    assert delivery_repository.list(offset=1, limit=1) == [second_delivery]
    assert delivery_repository.list(notification_id=notification.id) == [
        second_delivery,
        first_delivery,
    ]
    assert delivery_repository.list(channel=NotificationChannel.EMAIL.value) == [
        second_delivery
    ]
    assert delivery_repository.list(provider=NotificationProvider.WEBHOOK.value) == [
        third_delivery
    ]
    assert delivery_repository.list(provider_message_id="message-001") == [
        first_delivery
    ]
    assert delivery_repository.list(status=NotificationDeliveryStatus.FAILED.value) == [
        third_delivery
    ]
    assert delivery_repository.list(
        created_from=datetime(2026, 7, 5, 10, 0, 0),
    ) == [third_delivery, second_delivery]
    assert delivery_repository.list(
        created_to=datetime(2026, 7, 5, 10, 0, 0),
    ) == [second_delivery, first_delivery]
    assert delivery_repository.list(
        last_attempt_from=datetime(2026, 7, 5, 11, 0, 0),
    ) == [third_delivery]
    assert delivery_repository.list(
        last_attempt_to=datetime(2026, 7, 5, 10, 30, 0),
    ) == [second_delivery]
    assert delivery_repository.list(
        failed_from=datetime(2026, 7, 5, 11, 0, 0),
    ) == [third_delivery]
    assert delivery_repository.list(
        failed_to=datetime(2026, 7, 5, 11, 30, 0),
    ) == [third_delivery]
    assert delivery_repository.list(provider="missing") == []

    assert delivery_repository.count() == 3
    assert delivery_repository.count(notification_id=notification.id) == 2
    assert delivery_repository.count(channel=NotificationChannel.IN_APP.value) == 1
    assert delivery_repository.count(provider=NotificationProvider.SMTP.value) == 1
    assert delivery_repository.count(status=NotificationDeliveryStatus.PENDING.value) == 1
    assert delivery_repository.count(provider_message_id="missing") == 0

    delivered_at = datetime(2026, 7, 5, 12, 15, 0)
    updated_delivery = delivery_repository.update(
        first_delivery.id,
        {
            "channel": NotificationChannel.EMAIL.value,
            "provider": NotificationProvider.SMTP.value,
            "provider_message_id": "message-updated",
            "status": NotificationDeliveryStatus.SENT.value,
            "attempt_count": 1,
            "last_attempt_at": datetime(2026, 7, 5, 12, 10, 0),
            "provider_response": {"accepted": True},
        },
    )

    assert updated_delivery is first_delivery
    assert first_delivery.delivery_uuid == original_uuid
    assert delivery_repository.get_by_uuid(original_uuid) == first_delivery
    assert first_delivery.channel == NotificationChannel.EMAIL.value
    assert first_delivery.provider == NotificationProvider.SMTP.value
    assert first_delivery.provider_message_id == "message-updated"
    assert first_delivery.attempt_count == 1
    assert first_delivery.provider_response == {"accepted": True}

    marked_delivery = delivery_repository.mark_status(
        first_delivery.id,
        NotificationDeliveryStatus.DELIVERED.value,
        last_attempt_at=datetime(2026, 7, 5, 12, 20, 0),
        delivered_at=delivered_at,
        provider_message_id="message-delivered",
        provider_response={"delivered": True},
    )

    assert marked_delivery is first_delivery
    assert first_delivery.status == NotificationDeliveryStatus.DELIVERED.value
    assert first_delivery.delivered_at == delivered_at
    assert first_delivery.provider_message_id == "message-delivered"
    assert first_delivery.provider_response == {"delivered": True}

    assert delivery_repository.update(
        999,
        {"status": NotificationDeliveryStatus.FAILED.value},
    ) is None
    assert delivery_repository.mark_status(
        999,
        NotificationDeliveryStatus.FAILED.value,
    ) is None
    with pytest.raises(
        ValueError,
        match="Unsupported notification delivery update fields: notification_id",
    ):
        delivery_repository.update(
            first_delivery.id,
            {"notification_id": other_notification.id},
        )


def test_aggregate_repository_and_delivery_access_after_notification_soft_delete(
    db_session: Session,
) -> None:
    repository = NotificationsRepository(db_session)
    recipient = create_test_user(db_session, "notifications-aggregate-recipient")
    notification = create_notification(
        repository.notifications,
        recipient_user_id=recipient.id,
    )
    delivery = create_delivery(
        repository.deliveries,
        notification_id=notification.id,
        channel=NotificationChannel.EMAIL.value,
        provider=NotificationProvider.SMTP.value,
    )

    assert repository.db is db_session
    assert isinstance(repository.notifications, NotificationRepository)
    assert isinstance(repository.deliveries, NotificationDeliveryRepository)
    assert repository.health() is True
    assert repository.notifications.health() is True
    assert repository.deliveries.health() is True
    assert repository.notifications.get_by_id(notification.id) == notification
    assert repository.deliveries.get_by_id(delivery.id) == delivery
    assert delivery.notification_id == notification.id
    assert delivery.delivery_uuid != notification.notification_uuid

    assert repository.notifications.delete(notification.id) is True
    assert repository.notifications.get_by_id(notification.id) is None
    assert repository.notifications.get_by_id(
        notification.id,
        include_deleted=True,
    ) == notification
    assert repository.deliveries.get_by_id(delivery.id) == delivery
    assert repository.deliveries.list(notification_id=notification.id) == [delivery]
