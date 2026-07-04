from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.modules.user_management.models import (
    UserManagementAuditEvent,
    UserManagementProfile,
    UserManagementRoleAssignment,
)
from app.modules.user_management.repository import UserManagementRepository


def enable_foreign_keys(db_session: Session) -> None:
    db_session.execute(text("PRAGMA foreign_keys=ON"))


def create_test_user(db_session: Session, username: str = "repository-user") -> User:
    user = User(
        username=username,
        full_name="Repository User",
        password_hash="not-used",
        role="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_profile_create_read_update_deactivate_and_missing_results(
    db_session: Session,
) -> None:
    repository = UserManagementRepository(db_session)
    user = create_test_user(db_session)

    profile = repository.profiles.create(
        UserManagementProfile(
            user_id=user.id,
            display_name="Initial Name",
            personnel_number="PN-001",
            job_title="Operator",
            phone_number="+380000000001",
            notes="Created in repository test",
        ),
    )

    assert profile.id is not None
    assert repository.profiles.list() == [profile]
    assert repository.profiles.list_active() == [profile]
    assert repository.profiles.get_by_id(profile.id) == profile
    assert repository.profiles.get_by_user_id(user.id) == profile
    assert repository.profiles.get_by_id(999) is None
    assert repository.profiles.get_by_user_id(999) is None

    updated_profile = repository.profiles.update(
        profile.id,
        {
            "display_name": "Updated Name",
            "job_title": "Senior Operator",
            "is_active": False,
        },
    )

    assert updated_profile is profile
    assert profile.display_name == "Updated Name"
    assert profile.job_title == "Senior Operator"
    assert profile.personnel_number == "PN-001"
    assert profile.is_active is False
    assert repository.profiles.list_active() == []
    assert repository.profiles.update(999, {"display_name": "Missing"}) is None


def test_profile_duplicate_user_and_foreign_key_failures_roll_back_cleanly(
    db_session: Session,
) -> None:
    enable_foreign_keys(db_session)
    repository = UserManagementRepository(db_session)
    user = create_test_user(db_session)
    original_profile = repository.profiles.create(UserManagementProfile(user_id=user.id))
    db_session.commit()

    with pytest.raises(IntegrityError):
        repository.profiles.create(
            UserManagementProfile(
                user_id=user.id,
                display_name="Duplicate",
            ),
        )

    db_session.rollback()
    assert repository.profiles.get_by_user_id(user.id) == original_profile

    with pytest.raises(IntegrityError):
        repository.profiles.create(UserManagementProfile(user_id=999))

    db_session.rollback()
    updated_profile = repository.profiles.update(
        original_profile.id,
        {"display_name": "After rollback"},
    )

    assert updated_profile is original_profile
    assert original_profile.display_name == "After rollback"
    assert repository.profiles.list() == [original_profile]


def test_profile_create_rolls_back_uncommitted_database_state(
    db_session: Session,
) -> None:
    repository = UserManagementRepository(db_session)
    user = create_test_user(db_session)
    profile = repository.profiles.create(UserManagementProfile(user_id=user.id))
    profile_id = profile.id

    db_session.rollback()

    assert repository.profiles.get_by_id(profile_id) is None
    assert repository.profiles.list() == []


def test_role_assignment_create_list_by_user_revoke_and_missing_results(
    db_session: Session,
) -> None:
    repository = UserManagementRepository(db_session)
    user = create_test_user(db_session)
    assigned_by = create_test_user(db_session, "role-granter")

    assignment = repository.role_assignments.create(
        UserManagementRoleAssignment(
            user_id=user.id,
            role_code="document.manager",
            scope_type="department",
            scope_id=10,
            assigned_by_user_id=assigned_by.id,
        ),
    )
    other_assignment = repository.role_assignments.create(
        UserManagementRoleAssignment(
            user_id=assigned_by.id,
            role_code="audit.reader",
            scope_type="department",
            scope_id=20,
        ),
    )

    assert repository.role_assignments.list() == [assignment, other_assignment]
    assert repository.role_assignments.list_active() == [assignment, other_assignment]
    assert repository.role_assignments.get_by_id(assignment.id) == assignment
    assert repository.role_assignments.list_by_user_id(user.id) == [assignment]
    assert repository.role_assignments.list_active_by_user_id(user.id) == [assignment]
    assert (
        repository.role_assignments.get_by_scope(
            user.id,
            "document.manager",
            "department",
            10,
        )
        == assignment
    )
    assert repository.role_assignments.get_by_id(999) is None

    revoked_at = datetime(2026, 7, 4, 12, 0, tzinfo=timezone.utc)
    revoked_assignment = repository.role_assignments.revoke(
        assignment.id,
        {
            "is_active": False,
            "revoked_at": revoked_at,
        },
    )

    assert revoked_assignment is assignment
    assert assignment.is_active is False
    assert assignment.revoked_at == revoked_at
    assert repository.role_assignments.list_by_user_id(user.id) == [assignment]
    assert repository.role_assignments.list_active_by_user_id(user.id) == []
    assert repository.role_assignments.revoke(999, {"is_active": False}) is None


def test_role_assignment_duplicate_scope_and_foreign_key_failures(
    db_session: Session,
) -> None:
    enable_foreign_keys(db_session)
    repository = UserManagementRepository(db_session)
    user = create_test_user(db_session)
    assignment = repository.role_assignments.create(
        UserManagementRoleAssignment(
            user_id=user.id,
            role_code="document.manager",
            scope_type="department",
            scope_id=10,
        ),
    )
    db_session.commit()

    with pytest.raises(IntegrityError):
        repository.role_assignments.create(
            UserManagementRoleAssignment(
                user_id=user.id,
                role_code="document.manager",
                scope_type="department",
                scope_id=10,
            ),
        )

    db_session.rollback()
    assert repository.role_assignments.list() == [assignment]

    with pytest.raises(IntegrityError):
        repository.role_assignments.create(
            UserManagementRoleAssignment(
                user_id=999,
                role_code="missing-user",
            ),
        )

    db_session.rollback()
    assert repository.role_assignments.list() == [assignment]


def test_audit_event_create_list_by_user_and_descending_order(
    db_session: Session,
) -> None:
    repository = UserManagementRepository(db_session)
    actor = create_test_user(db_session, "audit-actor")
    target = create_test_user(db_session, "audit-target")
    other_target = create_test_user(db_session, "audit-other-target")

    first_event = repository.audit_events.create(
        UserManagementAuditEvent(
            actor_user_id=actor.id,
            target_user_id=target.id,
            event_type="profile.created",
            summary="Profile created",
            details={"field": "value"},
        ),
    )
    second_event = repository.audit_events.create(
        UserManagementAuditEvent(
            actor_user_id=actor.id,
            target_user_id=target.id,
            event_type="role.assigned",
            summary="Role assigned",
        ),
    )
    other_event = repository.audit_events.create(
        UserManagementAuditEvent(
            actor_user_id=actor.id,
            target_user_id=other_target.id,
            event_type="profile.updated",
        ),
    )

    assert repository.audit_events.get_by_id(first_event.id) == first_event
    assert repository.audit_events.get_by_id(999) is None
    assert repository.audit_events.list() == [other_event, second_event, first_event]
    assert repository.audit_events.list_by_actor_user_id(actor.id) == [
        other_event,
        second_event,
        first_event,
    ]
    assert repository.audit_events.list_by_target_user_id(target.id) == [
        second_event,
        first_event,
    ]
    assert repository.audit_events.list_by_target_user_id(999) == []
    assert second_event.details is None


def test_audit_event_foreign_key_failure_preserves_database_state(
    db_session: Session,
) -> None:
    enable_foreign_keys(db_session)
    repository = UserManagementRepository(db_session)
    actor = create_test_user(db_session)
    existing_event = repository.audit_events.create(
        UserManagementAuditEvent(
            actor_user_id=actor.id,
            event_type="profile.created",
        ),
    )
    db_session.commit()

    with pytest.raises(IntegrityError):
        repository.audit_events.create(
            UserManagementAuditEvent(
                actor_user_id=actor.id,
                target_user_id=999,
                event_type="profile.updated",
            ),
        )

    db_session.rollback()
    assert repository.audit_events.list() == [existing_event]
