"""Repository skeletons for the notifications module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.notifications.models import (
    Notification,
    NotificationDelivery,
)


class NotificationRepository:
    """Persistence operations for notifications."""

    _mutable_fields = frozenset(
        {
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
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification

    def create_notification(self, notification: Notification) -> Notification:
        return self.create(notification)

    def get_by_id(
        self,
        notification_id: int,
        *,
        include_deleted: bool = False,
    ) -> Notification | None:
        notification = self.db.get(Notification, notification_id)
        if (
            notification is not None
            and notification.deleted_at is not None
            and not include_deleted
        ):
            return None
        return notification

    def get_by_uuid(
        self,
        notification_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> Notification | None:
        query = select(Notification).where(
            Notification.notification_uuid == notification_uuid,
        )
        if not include_deleted:
            query = query.where(Notification.deleted_at.is_(None))
        return self.db.scalar(query)

    def list(
        self,
        *,
        recipient_user_id: int | None = None,
        actor_user_id: int | None = None,
        type: str | None = None,
        channel: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        correlation_id: str | None = None,
        request_id: str | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        sent_from: datetime | None = None,
        sent_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Notification]:
        query = self._build_query(
            recipient_user_id=recipient_user_id,
            actor_user_id=actor_user_id,
            type=type,
            channel=channel,
            priority=priority,
            status=status,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            request_id=request_id,
            scheduled_from=scheduled_from,
            scheduled_to=scheduled_to,
            sent_from=sent_from,
            sent_to=sent_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        ).order_by(Notification.created_at.desc(), Notification.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        recipient_user_id: int | None = None,
        actor_user_id: int | None = None,
        type: str | None = None,
        channel: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        correlation_id: str | None = None,
        request_id: str | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        sent_from: datetime | None = None,
        sent_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        query = self._build_query(
            recipient_user_id=recipient_user_id,
            actor_user_id=actor_user_id,
            type=type,
            channel=channel,
            priority=priority,
            status=status,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            request_id=request_id,
            scheduled_from=scheduled_from,
            scheduled_to=scheduled_to,
            sent_from=sent_from,
            sent_to=sent_to,
            created_from=created_from,
            created_to=created_to,
            include_deleted=include_deleted,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        notification_id: int,
        values: Mapping[str, object],
    ) -> Notification | None:
        notification = self.get_by_id(notification_id)
        if notification is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported notification update fields: {fields}")

        for field, value in values.items():
            setattr(notification, field, value)

        self.db.flush()
        return notification

    def delete(self, notification_id: int) -> bool:
        notification = self.get_by_id(notification_id)
        if notification is None:
            return False

        notification.deleted_at = datetime.now(timezone.utc)
        self.db.flush()
        return True

    def mark_deleted(self, notification_id: int) -> bool:
        return self.delete(notification_id)

    def exists(self, notification_id: int, *, include_deleted: bool = False) -> bool:
        return self.get_by_id(
            notification_id,
            include_deleted=include_deleted,
        ) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        recipient_user_id: int | None = None,
        actor_user_id: int | None = None,
        type: str | None = None,
        channel: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        correlation_id: str | None = None,
        request_id: str | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
        sent_from: datetime | None = None,
        sent_to: datetime | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        include_deleted: bool = False,
    ) -> Select[tuple[Notification]]:
        query = select(Notification)

        if not include_deleted:
            query = query.where(Notification.deleted_at.is_(None))
        if recipient_user_id is not None:
            query = query.where(Notification.recipient_user_id == recipient_user_id)
        if actor_user_id is not None:
            query = query.where(Notification.actor_user_id == actor_user_id)
        if type is not None:
            query = query.where(Notification.type == type)
        if channel is not None:
            query = query.where(Notification.channel == channel)
        if priority is not None:
            query = query.where(Notification.priority == priority)
        if status is not None:
            query = query.where(Notification.status == status)
        if entity_type is not None:
            query = query.where(Notification.entity_type == entity_type)
        if entity_id is not None:
            query = query.where(Notification.entity_id == entity_id)
        if correlation_id is not None:
            query = query.where(Notification.correlation_id == correlation_id)
        if request_id is not None:
            query = query.where(Notification.request_id == request_id)
        if scheduled_from is not None:
            query = query.where(Notification.scheduled_at >= scheduled_from)
        if scheduled_to is not None:
            query = query.where(Notification.scheduled_at <= scheduled_to)
        if sent_from is not None:
            query = query.where(Notification.sent_at >= sent_from)
        if sent_to is not None:
            query = query.where(Notification.sent_at <= sent_to)
        if created_from is not None:
            query = query.where(Notification.created_at >= created_from)
        if created_to is not None:
            query = query.where(Notification.created_at <= created_to)

        return query


class NotificationDeliveryRepository:
    """Persistence operations for notification delivery attempts."""

    _mutable_fields = frozenset(
        {
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
        },
    )

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, delivery: NotificationDelivery) -> NotificationDelivery:
        self.db.add(delivery)
        self.db.flush()
        return delivery

    def create_delivery(self, delivery: NotificationDelivery) -> NotificationDelivery:
        return self.create(delivery)

    def get_by_id(self, delivery_id: int) -> NotificationDelivery | None:
        return self.db.get(NotificationDelivery, delivery_id)

    def get_by_uuid(self, delivery_uuid: UUID) -> NotificationDelivery | None:
        return self.db.scalar(
            select(NotificationDelivery).where(
                NotificationDelivery.delivery_uuid == delivery_uuid,
            ),
        )

    def list(
        self,
        *,
        notification_id: int | None = None,
        channel: str | None = None,
        provider: str | None = None,
        provider_message_id: str | None = None,
        status: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        last_attempt_from: datetime | None = None,
        last_attempt_to: datetime | None = None,
        delivered_from: datetime | None = None,
        delivered_to: datetime | None = None,
        failed_from: datetime | None = None,
        failed_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[NotificationDelivery]:
        query = self._build_query(
            notification_id=notification_id,
            channel=channel,
            provider=provider,
            provider_message_id=provider_message_id,
            status=status,
            created_from=created_from,
            created_to=created_to,
            last_attempt_from=last_attempt_from,
            last_attempt_to=last_attempt_to,
            delivered_from=delivered_from,
            delivered_to=delivered_to,
            failed_from=failed_from,
            failed_to=failed_to,
        ).order_by(NotificationDelivery.created_at.desc(), NotificationDelivery.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        notification_id: int | None = None,
        channel: str | None = None,
        provider: str | None = None,
        provider_message_id: str | None = None,
        status: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        last_attempt_from: datetime | None = None,
        last_attempt_to: datetime | None = None,
        delivered_from: datetime | None = None,
        delivered_to: datetime | None = None,
        failed_from: datetime | None = None,
        failed_to: datetime | None = None,
    ) -> int:
        query = self._build_query(
            notification_id=notification_id,
            channel=channel,
            provider=provider,
            provider_message_id=provider_message_id,
            status=status,
            created_from=created_from,
            created_to=created_to,
            last_attempt_from=last_attempt_from,
            last_attempt_to=last_attempt_to,
            delivered_from=delivered_from,
            delivered_to=delivered_to,
            failed_from=failed_from,
            failed_to=failed_to,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def update(
        self,
        delivery_id: int,
        values: Mapping[str, object],
    ) -> NotificationDelivery | None:
        delivery = self.get_by_id(delivery_id)
        if delivery is None:
            return None

        unsupported_fields = set(values) - self._mutable_fields
        if unsupported_fields:
            fields = ", ".join(sorted(unsupported_fields))
            raise ValueError(f"Unsupported notification delivery update fields: {fields}")

        for field, value in values.items():
            setattr(delivery, field, value)

        self.db.flush()
        return delivery

    def mark_status(
        self,
        delivery_id: int,
        status: str,
        *,
        last_attempt_at: datetime | None = None,
        delivered_at: datetime | None = None,
        failed_at: datetime | None = None,
        failure_reason: str | None = None,
        provider_message_id: str | None = None,
        provider_response: Mapping[str, object] | None = None,
    ) -> NotificationDelivery | None:
        values: dict[str, object] = {"status": status}

        if last_attempt_at is not None:
            values["last_attempt_at"] = last_attempt_at
        if delivered_at is not None:
            values["delivered_at"] = delivered_at
        if failed_at is not None:
            values["failed_at"] = failed_at
        if failure_reason is not None:
            values["failure_reason"] = failure_reason
        if provider_message_id is not None:
            values["provider_message_id"] = provider_message_id
        if provider_response is not None:
            values["provider_response"] = dict(provider_response)

        return self.update(delivery_id, values)

    def exists(self, delivery_id: int) -> bool:
        return self.get_by_id(delivery_id) is not None

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1

    def _build_query(
        self,
        *,
        notification_id: int | None = None,
        channel: str | None = None,
        provider: str | None = None,
        provider_message_id: str | None = None,
        status: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        last_attempt_from: datetime | None = None,
        last_attempt_to: datetime | None = None,
        delivered_from: datetime | None = None,
        delivered_to: datetime | None = None,
        failed_from: datetime | None = None,
        failed_to: datetime | None = None,
    ) -> Select[tuple[NotificationDelivery]]:
        query = select(NotificationDelivery)

        if notification_id is not None:
            query = query.where(NotificationDelivery.notification_id == notification_id)
        if channel is not None:
            query = query.where(NotificationDelivery.channel == channel)
        if provider is not None:
            query = query.where(NotificationDelivery.provider == provider)
        if provider_message_id is not None:
            query = query.where(
                NotificationDelivery.provider_message_id == provider_message_id,
            )
        if status is not None:
            query = query.where(NotificationDelivery.status == status)
        if created_from is not None:
            query = query.where(NotificationDelivery.created_at >= created_from)
        if created_to is not None:
            query = query.where(NotificationDelivery.created_at <= created_to)
        if last_attempt_from is not None:
            query = query.where(NotificationDelivery.last_attempt_at >= last_attempt_from)
        if last_attempt_to is not None:
            query = query.where(NotificationDelivery.last_attempt_at <= last_attempt_to)
        if delivered_from is not None:
            query = query.where(NotificationDelivery.delivered_at >= delivered_from)
        if delivered_to is not None:
            query = query.where(NotificationDelivery.delivered_at <= delivered_to)
        if failed_from is not None:
            query = query.where(NotificationDelivery.failed_at >= failed_from)
        if failed_to is not None:
            query = query.where(NotificationDelivery.failed_at <= failed_to)

        return query


class NotificationsRepository:
    """Persistence boundary for notifications data."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.notifications = NotificationRepository(db)
        self.deliveries = NotificationDeliveryRepository(db)

    def health(self) -> bool:
        return self.db.scalar(select(1)) == 1


__all__ = [
    "NotificationDeliveryRepository",
    "NotificationRepository",
    "NotificationsRepository",
]
