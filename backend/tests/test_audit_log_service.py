from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.modules.audit_log.models import AuditLogEvent
from app.modules.audit_log.repository import AuditLogRepository
from app.modules.audit_log.service import AuditLogService


@pytest.fixture()
def service(db_session: Session) -> AuditLogService:
    return AuditLogService(AuditLogRepository(db_session))


def create_test_user(db_session: Session, username: str = "audit-service-user") -> User:
    user = User(
        username=username,
        full_name="Audit Service User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_audit_event(
    service: AuditLogService,
    *,
    event_type: str = "document.created",
    entity_type: str | None = "document",
    entity_id: str | None = "DOC-SVC-001",
    actor_user_id: int | None = None,
    actor_username: str | None = "audit-service-user",
    action: str = "create",
    status: str = "success",
    request_id: str | None = "request-service-001",
    correlation_id: str | None = "correlation-service-001",
    created_at: datetime | None = None,
) -> AuditLogEvent:
    return service.create_event(
        AuditLogEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            action=action,
            status=status,
            ip_address="127.0.0.1",
            user_agent="pytest-service",
            request_id=request_id,
            correlation_id=correlation_id,
            payload={"document_number": entity_id, "source": "service-test"},
            before_state={"status": "draft"},
            after_state={"status": "active"},
            created_at=created_at,
        ),
    )


def test_audit_log_service_create_lookup_uuid_and_json_state(
    service: AuditLogService,
    db_session: Session,
) -> None:
    actor = create_test_user(db_session)

    event = create_audit_event(
        service,
        actor_user_id=actor.id,
        actor_username=actor.username,
    )
    written_event = service.write_event(
        AuditLogEvent(
            event_type="document.reviewed",
            entity_type="document",
            entity_id="DOC-SVC-002",
            actor_user_id=actor.id,
            actor_username=actor.username,
            action="review",
            payload={"decision": "approved"},
        ),
    )

    assert event.id is not None
    assert event.event_uuid is not None
    assert written_event.id is not None
    assert service.get_event(event.id) == event
    assert service.get_event_by_uuid(event.event_uuid) == event
    assert service.require_event(event.id) == event
    assert event.payload == {
        "document_number": "DOC-SVC-001",
        "source": "service-test",
    }
    assert event.before_state == {"status": "draft"}
    assert event.after_state == {"status": "active"}
    assert written_event.payload == {"decision": "approved"}


def test_audit_log_service_missing_event_behavior(
    service: AuditLogService,
) -> None:
    assert service.get_event(999) is None
    assert service.get_event_by_uuid(uuid4()) is None

    with pytest.raises(ValueError, match="Audit log event not found"):
        service.require_event(999)


def test_audit_log_service_list_search_count_filters_and_pagination(
    service: AuditLogService,
    db_session: Session,
) -> None:
    actor = create_test_user(db_session, "audit-service-actor")
    other_actor = create_test_user(db_session, "audit-service-other")

    first_event = create_audit_event(
        service,
        event_type="document.created",
        entity_type="document",
        entity_id="DOC-SVC-001",
        actor_user_id=actor.id,
        actor_username=actor.username,
        action="create",
        status="success",
        request_id="request-service-001",
        correlation_id="correlation-service-docs",
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second_event = create_audit_event(
        service,
        event_type="document.updated",
        entity_type="document",
        entity_id="DOC-SVC-001",
        actor_user_id=actor.id,
        actor_username=actor.username,
        action="update",
        status="failure",
        request_id="request-service-002",
        correlation_id="correlation-service-docs",
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third_event = create_audit_event(
        service,
        event_type="user.logged_in",
        entity_type="user",
        entity_id=str(other_actor.id),
        actor_user_id=other_actor.id,
        actor_username=other_actor.username,
        action="login",
        status="success",
        request_id="request-service-003",
        correlation_id="correlation-service-auth",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert service.list_events() == [third_event, second_event, first_event]
    assert service.search_events(entity_type="document") == [
        second_event,
        first_event,
    ]
    assert service.search_events(entity_id="DOC-SVC-001") == [
        second_event,
        first_event,
    ]
    assert service.search_events(actor_user_id=actor.id) == [
        second_event,
        first_event,
    ]
    assert service.search_events(action="update") == [second_event]
    assert service.search_events(status="failure") == [second_event]
    assert service.search_events(request_id="request-service-003") == [third_event]
    assert service.search_events(correlation_id="correlation-service-docs") == [
        second_event,
        first_event,
    ]
    assert service.search_events(
        created_from=datetime(2026, 7, 5, 10, 0, 0),
        limit=1,
    ) == [third_event]
    assert service.list_events(offset=1, limit=1) == [second_event]
    assert service.search_events(entity_type="missing") == []

    assert service.count_events() == 3
    assert service.count_events(actor_user_id=actor.id) == 2
    assert service.count_events(entity_type="document", status="failure") == 1
    assert service.count_events(correlation_id="missing") == 0


def test_audit_log_service_health_contract(service: AuditLogService) -> None:
    assert service.health() == {"status": "ok"}
