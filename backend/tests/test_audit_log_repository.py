from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import User
from app.modules.audit_log.models import AuditLogEvent
from app.modules.audit_log.repository import AuditLogRepository


def create_test_user(db_session: Session, username: str = "audit-repository-user") -> User:
    user = User(
        username=username,
        full_name="Audit Repository User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_audit_event(
    repository: AuditLogRepository,
    *,
    event_type: str = "document.created",
    entity_type: str | None = "document",
    entity_id: str | None = "DOC-001",
    actor_user_id: int | None = None,
    actor_username: str | None = "audit-user",
    action: str = "create",
    status: str = "success",
    request_id: str | None = "request-001",
    correlation_id: str | None = "correlation-001",
    created_at: datetime | None = None,
) -> AuditLogEvent:
    return repository.create(
        AuditLogEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            action=action,
            status=status,
            ip_address="127.0.0.1",
            user_agent="pytest",
            request_id=request_id,
            correlation_id=correlation_id,
            payload={"source": "repository-test"},
            before_state={"status": "draft"},
            after_state={"status": "active"},
            created_at=created_at,
        ),
    )


def test_audit_log_event_create_lookup_by_id_uuid_and_missing_results(
    db_session: Session,
) -> None:
    repository = AuditLogRepository(db_session)
    actor = create_test_user(db_session)

    event = create_audit_event(
        repository,
        actor_user_id=actor.id,
        actor_username=actor.username,
    )
    alias_event = repository.create_event(
        AuditLogEvent(
            event_type="document.updated",
            entity_type="document",
            entity_id="DOC-002",
            actor_user_id=actor.id,
            actor_username=actor.username,
            action="update",
            payload={"field": "title"},
        ),
    )

    assert event.id is not None
    assert event.event_uuid is not None
    assert alias_event.id is not None
    assert repository.get_by_id(event.id) == event
    assert repository.get_by_uuid(event.event_uuid) == event
    assert repository.get_by_id(999) is None
    assert repository.get_by_uuid(uuid4()) is None
    assert event.payload == {"source": "repository-test"}
    assert event.before_state == {"status": "draft"}
    assert event.after_state == {"status": "active"}


def test_audit_log_event_list_filters_count_ordering_and_pagination(
    db_session: Session,
) -> None:
    repository = AuditLogRepository(db_session)
    actor = create_test_user(db_session, "audit-filter-actor")
    other_actor = create_test_user(db_session, "audit-filter-other")

    first_event = create_audit_event(
        repository,
        event_type="document.created",
        entity_type="document",
        entity_id="DOC-001",
        actor_user_id=actor.id,
        actor_username=actor.username,
        action="create",
        status="success",
        request_id="request-001",
        correlation_id="correlation-docs",
        created_at=datetime(2026, 7, 5, 9, 0, 0),
    )
    second_event = create_audit_event(
        repository,
        event_type="document.updated",
        entity_type="document",
        entity_id="DOC-001",
        actor_user_id=actor.id,
        actor_username=actor.username,
        action="update",
        status="failure",
        request_id="request-002",
        correlation_id="correlation-docs",
        created_at=datetime(2026, 7, 5, 10, 0, 0),
    )
    third_event = create_audit_event(
        repository,
        event_type="user.logged_in",
        entity_type="user",
        entity_id=str(other_actor.id),
        actor_user_id=other_actor.id,
        actor_username=other_actor.username,
        action="login",
        status="success",
        request_id="request-003",
        correlation_id="correlation-auth",
        created_at=datetime(2026, 7, 5, 11, 0, 0),
    )

    assert repository.list() == [third_event, second_event, first_event]
    assert repository.list(limit=2) == [third_event, second_event]
    assert repository.list(offset=1, limit=1) == [second_event]

    assert repository.list(actor_user_id=actor.id) == [second_event, first_event]
    assert repository.list(actor_username=actor.username) == [second_event, first_event]
    assert repository.list(event_type="document.created") == [first_event]
    assert repository.list(action="update") == [second_event]
    assert repository.list(status="failure") == [second_event]
    assert repository.list(entity_type="document") == [second_event, first_event]
    assert repository.list(entity_id="DOC-001") == [second_event, first_event]
    assert repository.list(request_id="request-003") == [third_event]
    assert repository.list(correlation_id="correlation-docs") == [
        second_event,
        first_event,
    ]
    assert repository.list(created_from=datetime(2026, 7, 5, 10, 0, 0)) == [
        third_event,
        second_event,
    ]
    assert repository.list(created_to=datetime(2026, 7, 5, 10, 0, 0)) == [
        second_event,
        first_event,
    ]
    assert repository.list(entity_type="missing") == []

    assert repository.count() == 3
    assert repository.count(actor_user_id=actor.id) == 2
    assert repository.count(status="success") == 2
    assert repository.count(entity_type="document", status="failure") == 1
    assert repository.count(correlation_id="missing") == 0
