"""Service layer skeleton for the audit log module."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.modules.audit_log.models import AuditLogEvent
from app.modules.audit_log.repository import AuditLogRepository


class AuditLogService:
    """Business boundary for audit log operations."""

    def __init__(self, repository: AuditLogRepository) -> None:
        self.repository = repository

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def create_event(self, audit_event: AuditLogEvent) -> AuditLogEvent:
        return self.repository.create_event(audit_event)

    def write_event(self, audit_event: AuditLogEvent) -> AuditLogEvent:
        return self.create_event(audit_event)

    def list_events(
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
        return self.repository.list(
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
            limit=limit,
            offset=offset,
        )

    def search_events(
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
        return self.list_events(
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
            limit=limit,
            offset=offset,
        )

    def count_events(
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
        return self.repository.count(
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

    def get_event(self, audit_event_id: int) -> AuditLogEvent | None:
        return self.repository.get_by_id(audit_event_id)

    def get_event_by_uuid(self, event_uuid: UUID) -> AuditLogEvent | None:
        return self.repository.get_by_uuid(event_uuid)

    def require_event(self, audit_event_id: int) -> AuditLogEvent:
        return self._require_event(audit_event_id)

    def _require_event(self, audit_event_id: int) -> AuditLogEvent:
        audit_event = self.repository.get_by_id(audit_event_id)
        if audit_event is None:
            raise ValueError("Audit log event not found")
        return audit_event
