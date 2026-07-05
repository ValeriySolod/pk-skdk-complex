"""Service layer for the notifications module."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from app.modules.notifications.models import Notification, NotificationDelivery
from app.modules.notifications.repository import NotificationsRepository


class NotificationsService:
    """Business boundary for notification workflows."""

    def __init__(self, repository: NotificationsRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        status = "ok" if self.repository.health() else "degraded"
        return {"status": status}

    def create_notification(self, notification: Notification) -> Notification:
        return self.repository.notifications.create_notification(notification)

    def create(self, notification: Notification) -> Notification:
        return self.create_notification(notification)

    def get_notification(
        self,
        notification_id: int,
        *,
        include_deleted: bool = False,
    ) -> Notification | None:
        return self.repository.notifications.get_by_id(
            notification_id,
            include_deleted=include_deleted,
        )

    def get_by_id(
        self,
        notification_id: int,
        *,
        include_deleted: bool = False,
    ) -> Notification | None:
        return self.get_notification(
            notification_id,
            include_deleted=include_deleted,
        )

    def get_notification_by_uuid(
        self,
        notification_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> Notification | None:
        return self.repository.notifications.get_by_uuid(
            notification_uuid,
            include_deleted=include_deleted,
        )

    def get_by_uuid(
        self,
        notification_uuid: UUID,
        *,
        include_deleted: bool = False,
    ) -> Notification | None:
        return self.get_notification_by_uuid(
            notification_uuid,
            include_deleted=include_deleted,
        )

    def list_notifications(
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
        return self.repository.notifications.list(
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
            limit=limit,
            offset=offset,
        )

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
        return self.list_notifications(
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
            limit=limit,
            offset=offset,
        )

    def count_notifications(
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
        return self.repository.notifications.count(
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
        return self.count_notifications(
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

    def update_notification(
        self,
        notification_id: int,
        values: Mapping[str, object],
    ) -> Notification | None:
        return self.repository.notifications.update(notification_id, values)

    def update(
        self,
        notification_id: int,
        values: Mapping[str, object],
    ) -> Notification | None:
        return self.update_notification(notification_id, values)

    def mark_notification_deleted(self, notification_id: int) -> bool:
        return self.repository.notifications.mark_deleted(notification_id)

    def mark_deleted(self, notification_id: int) -> bool:
        return self.mark_notification_deleted(notification_id)

    def delete_notification(self, notification_id: int) -> bool:
        return self.repository.notifications.delete(notification_id)

    def delete(self, notification_id: int) -> bool:
        return self.delete_notification(notification_id)

    def notification_exists(
        self,
        notification_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        return self.repository.notifications.exists(
            notification_id,
            include_deleted=include_deleted,
        )

    def exists(
        self,
        notification_id: int,
        *,
        include_deleted: bool = False,
    ) -> bool:
        return self.notification_exists(
            notification_id,
            include_deleted=include_deleted,
        )

    def create_delivery(
        self,
        delivery: NotificationDelivery,
    ) -> NotificationDelivery:
        return self.repository.deliveries.create_delivery(delivery)

    def create_notification_delivery(
        self,
        delivery: NotificationDelivery,
    ) -> NotificationDelivery:
        return self.create_delivery(delivery)

    def get_delivery(self, delivery_id: int) -> NotificationDelivery | None:
        return self.repository.deliveries.get_by_id(delivery_id)

    def get_delivery_by_id(self, delivery_id: int) -> NotificationDelivery | None:
        return self.get_delivery(delivery_id)

    def delivery_exists(self, delivery_id: int) -> bool:
        return self.repository.deliveries.exists(delivery_id)

    def get_delivery_by_uuid(
        self,
        delivery_uuid: UUID,
    ) -> NotificationDelivery | None:
        return self.repository.deliveries.get_by_uuid(delivery_uuid)

    def list_deliveries(
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
        return self.repository.deliveries.list(
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
            limit=limit,
            offset=offset,
        )

    def count_deliveries(
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
        return self.repository.deliveries.count(
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

    def update_delivery(
        self,
        delivery_id: int,
        values: Mapping[str, object],
    ) -> NotificationDelivery | None:
        return self.repository.deliveries.update(delivery_id, values)

    def update_delivery_status(
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
        return self.repository.deliveries.mark_status(
            delivery_id,
            status,
            last_attempt_at=last_attempt_at,
            delivered_at=delivered_at,
            failed_at=failed_at,
            failure_reason=failure_reason,
            provider_message_id=provider_message_id,
            provider_response=provider_response,
        )

    def mark_delivery_status(
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
        return self.update_delivery_status(
            delivery_id,
            status,
            last_attempt_at=last_attempt_at,
            delivered_at=delivered_at,
            failed_at=failed_at,
            failure_reason=failure_reason,
            provider_message_id=provider_message_id,
            provider_response=provider_response,
        )



__all__ = ["NotificationsService"]
