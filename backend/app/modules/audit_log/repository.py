"""Repository skeleton for the audit log module."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.audit_log.models import AuditLogEvent


class AuditLogRepository:
    """Persistence operations for audit log events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, audit_event: AuditLogEvent) -> AuditLogEvent:
        self.db.add(audit_event)
        self.db.flush()
        return audit_event

    def create_event(self, audit_event: AuditLogEvent) -> AuditLogEvent:
        return self.create(audit_event)

    def get_by_id(self, audit_event_id: int) -> AuditLogEvent | None:
        return self.db.get(AuditLogEvent, audit_event_id)

    def get_by_uuid(self, event_uuid: UUID) -> AuditLogEvent | None:
        return self.db.scalar(
            select(AuditLogEvent).where(AuditLogEvent.event_uuid == event_uuid),
        )

    def list(
        self,
        *,
        actor_user_id: int | None = None,
        actor_username: str | None = None,
        event_type: str | None = None,
        action: str | None = None,
        status: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[AuditLogEvent]:
        query = self._build_query(
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            event_type=event_type,
            action=action,
            status=status,
            entity_type=entity_type,
            entity_id=entity_id,
            request_id=request_id,
            correlation_id=correlation_id,
            created_from=created_from,
            created_to=created_to,
        ).order_by(AuditLogEvent.created_at.desc(), AuditLogEvent.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return list(self.db.scalars(query).all())

    def count(
        self,
        *,
        actor_user_id: int | None = None,
        actor_username: str | None = None,
        event_type: str | None = None,
        action: str | None = None,
        status: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        query = self._build_query(
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            event_type=event_type,
            action=action,
            status=status,
            entity_type=entity_type,
            entity_id=entity_id,
            request_id=request_id,
            correlation_id=correlation_id,
            created_from=created_from,
            created_to=created_to,
        )
        return self.db.scalar(select(func.count()).select_from(query.subquery())) or 0

    def _build_query(
        self,
        *,
        actor_user_id: int | None = None,
        actor_username: str | None = None,
        event_type: str | None = None,
        action: str | None = None,
        status: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> Select[tuple[AuditLogEvent]]:
        query = select(AuditLogEvent)

        if actor_user_id is not None:
            query = query.where(AuditLogEvent.actor_user_id == actor_user_id)
        if actor_username is not None:
            query = query.where(AuditLogEvent.actor_username == actor_username)
        if event_type is not None:
            query = query.where(AuditLogEvent.event_type == event_type)
        if action is not None:
            query = query.where(AuditLogEvent.action == action)
        if status is not None:
            query = query.where(AuditLogEvent.status == status)
        if entity_type is not None:
            query = query.where(AuditLogEvent.entity_type == entity_type)
        if entity_id is not None:
            query = query.where(AuditLogEvent.entity_id == entity_id)
        if request_id is not None:
            query = query.where(AuditLogEvent.request_id == request_id)
        if correlation_id is not None:
            query = query.where(AuditLogEvent.correlation_id == correlation_id)
        if created_from is not None:
            query = query.where(AuditLogEvent.created_at >= created_from)
        if created_to is not None:
            query = query.where(AuditLogEvent.created_at <= created_to)

        return query


__all__ = ["AuditLogRepository"]
