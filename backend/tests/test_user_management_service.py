from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from app.models import User
from app.modules.user_management.repository import UserManagementRepository
from app.modules.user_management.schemas import (
    UserManagementAuditEventCreate,
    UserManagementProfileCreate,
    UserManagementProfileUpdate,
    UserManagementRoleAssignmentCreate,
    UserManagementRoleAssignmentUpdate,
)
from app.modules.user_management.service import UserManagementService


@pytest.fixture()
def service(db_session: Session) -> UserManagementService:
    return UserManagementService(UserManagementRepository(db_session))


def create_test_user(
    db_session: Session,
    username: str = "user-management-service-user",
    *,
    is_active: bool = True,
) -> User:
    user = User(
        username=username,
        full_name="User Management Service User",
        password_hash="not-used",
        role="test",
        is_active=is_active,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_profile_create_read_update_and_active_listing(
    db_session: Session,
    service: UserManagementService,
) -> None:
    user = create_test_user(db_session)

    profile = service.create_profile(
        UserManagementProfileCreate(
            user_id=user.id,
            display_name="Initial Name",
            personnel_number="PN-001",
            job_title="Operator",
            phone_number="+380000000001",
            notes="Created through service",
        ),
    )

    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.display_name == "Initial Name"
    assert service.get_profile(profile.id) == profile
    assert service.get_profile_by_user_id(user.id) == profile
    assert service.get_profile_by_user_id(999) is None
    assert service.list_profiles() == [profile]
    assert service.list_active_profiles() == [profile]

    updated_profile = service.update_profile(
        profile.id,
        UserManagementProfileUpdate(
            display_name="Updated Name",
            job_title="Senior Operator",
            is_active=False,
        ),
    )

    assert updated_profile is profile
    assert profile.display_name == "Updated Name"
    assert profile.job_title == "Senior Operator"
    assert profile.personnel_number == "PN-001"
    assert profile.is_active is False
    assert service.list_profiles() == [profile]
    assert service.list_active_profiles() == []
    assert service.update_profile(999, UserManagementProfileUpdate(notes="Missing")) is None


def test_profile_create_rejects_missing_user_and_duplicate_profile(
    db_session: Session,
    service: UserManagementService,
) -> None:
    user = create_test_user(db_session)
    service.create_profile(UserManagementProfileCreate(user_id=user.id))

    with pytest.raises(ValueError, match="User not found"):
        service.create_profile(UserManagementProfileCreate(user_id=999))

    with pytest.raises(ValueError, match="User profile already exists"):
        service.create_profile(
            UserManagementProfileCreate(
                user_id=user.id,
                display_name="Duplicate",
            ),
        )


def test_role_assignment_lifecycle_and_active_listing(
    db_session: Session,
    service: UserManagementService,
) -> None:
    user = create_test_user(db_session)
    assigner = create_test_user(db_session, "role-assigner")

    assignment = service.assign_role(
        UserManagementRoleAssignmentCreate(
            user_id=user.id,
            role_code="document.manager",
            scope_type="department",
            scope_id=10,
            assigned_by_user_id=assigner.id,
        ),
    )
    inactive_assignment = service.assign_role(
        UserManagementRoleAssignmentCreate(
            user_id=user.id,
            role_code="audit.reader",
            scope_type="department",
            scope_id=20,
            is_active=False,
        ),
    )

    assert assignment.id is not None
    assert assignment.user_id == user.id
    assert assignment.assigned_by_user_id == assigner.id
    assert assignment.is_active is True
    assert service.get_role_assignment(assignment.id) == assignment
    assert service.list_role_assignments() == [assignment, inactive_assignment]
    assert service.list_active_role_assignments() == [assignment]
    assert service.list_user_role_assignments(user.id) == [
        assignment,
        inactive_assignment,
    ]
    assert service.list_active_user_role_assignments(user.id) == [assignment]

    revoked_at = datetime(2026, 7, 4, 12, 0, tzinfo=timezone.utc)
    revoked_assignment = service.revoke_role_assignment(
        assignment.id,
        UserManagementRoleAssignmentUpdate(revoked_at=revoked_at),
    )

    assert revoked_assignment is assignment
    assert assignment.is_active is False
    assert assignment.revoked_at == revoked_at
    assert service.list_active_role_assignments() == []
    assert service.list_active_user_role_assignments(user.id) == []
    assert service.revoke_role_assignment(999) is None


def test_role_assignment_rejects_missing_user_and_duplicate_active_scope(
    db_session: Session,
    service: UserManagementService,
) -> None:
    user = create_test_user(db_session)
    assignment = service.create_role_assignment(
        UserManagementRoleAssignmentCreate(
            user_id=user.id,
            role_code="document.manager",
            scope_type="department",
            scope_id=10,
        ),
    )

    with pytest.raises(ValueError, match="User not found"):
        service.assign_role(
            UserManagementRoleAssignmentCreate(
                user_id=999,
                role_code="document.manager",
            ),
        )

    with pytest.raises(ValueError, match="Active role assignment already exists"):
        service.assign_role(
            UserManagementRoleAssignmentCreate(
                user_id=user.id,
                role_code="document.manager",
                scope_type="department",
                scope_id=10,
            ),
        )

    service.revoke_role_assignment(assignment.id)
    scoped_assignment = service.assign_role(
        UserManagementRoleAssignmentCreate(
            user_id=user.id,
            role_code="document.manager",
            scope_type="department",
            scope_id=20,
        ),
    )

    assert scoped_assignment.id is not None
    assert service.list_active_user_role_assignments(user.id) == [scoped_assignment]


def test_role_assignment_update_revalidates_active_scope(
    db_session: Session,
    service: UserManagementService,
) -> None:
    user = create_test_user(db_session)
    first_assignment = service.assign_role(
        UserManagementRoleAssignmentCreate(
            user_id=user.id,
            role_code="document.manager",
            scope_type="department",
            scope_id=10,
        ),
    )
    second_assignment = service.assign_role(
        UserManagementRoleAssignmentCreate(
            user_id=user.id,
            role_code="audit.reader",
            scope_type="department",
            scope_id=10,
        ),
    )

    with pytest.raises(ValueError, match="Active role assignment already exists"):
        service.update_role_assignment(
            second_assignment.id,
            UserManagementRoleAssignmentUpdate(role_code=first_assignment.role_code),
        )

    updated_assignment = service.update_role_assignment(
        second_assignment.id,
        UserManagementRoleAssignmentUpdate(is_active=False),
    )

    assert updated_assignment is second_assignment
    assert second_assignment.is_active is False
    assert service.update_role_assignment(999, UserManagementRoleAssignmentUpdate()) is None


def test_audit_event_create_list_and_filter_by_users(
    db_session: Session,
    service: UserManagementService,
) -> None:
    actor = create_test_user(db_session, "audit-actor")
    target = create_test_user(db_session, "audit-target")
    other_target = create_test_user(db_session, "audit-other-target")

    first_event = service.create_audit_event(
        UserManagementAuditEventCreate(
            actor_user_id=actor.id,
            target_user_id=target.id,
            event_type="profile.created",
            summary="Profile created",
            details={"source": "service-test"},
        ),
    )
    second_event = service.create_audit_event(
        UserManagementAuditEventCreate(
            actor_user_id=actor.id,
            target_user_id=target.id,
            event_type="role.assigned",
            summary="Role assigned",
        ),
    )
    other_event = service.create_audit_event(
        UserManagementAuditEventCreate(
            actor_user_id=actor.id,
            target_user_id=other_target.id,
            event_type="profile.updated",
        ),
    )

    assert first_event.id is not None
    assert first_event.actor_user_id == actor.id
    assert first_event.target_user_id == target.id
    assert first_event.event_type == "profile.created"
    assert first_event.summary == "Profile created"
    assert first_event.details == {"source": "service-test"}
    assert first_event.created_at is not None
    assert service.get_audit_event(first_event.id) == first_event
    assert service.get_audit_event(999) is None
    assert service.list_audit_events() == [other_event, second_event, first_event]
    assert service.list_audit_events_by_actor(actor.id) == [
        other_event,
        second_event,
        first_event,
    ]
    assert service.list_audit_events_by_target(target.id) == [
        second_event,
        first_event,
    ]
    assert service.list_audit_events_by_target(999) == []


def test_audit_event_rejects_missing_actor_or_target_user(
    db_session: Session,
    service: UserManagementService,
) -> None:
    actor = create_test_user(db_session)

    with pytest.raises(ValueError, match="User not found"):
        service.create_audit_event(
            UserManagementAuditEventCreate(
                actor_user_id=999,
                target_user_id=actor.id,
                event_type="profile.updated",
            ),
        )

    with pytest.raises(ValueError, match="User not found"):
        service.create_audit_event(
            UserManagementAuditEventCreate(
                actor_user_id=actor.id,
                target_user_id=999,
                event_type="profile.updated",
            ),
        )


def test_user_lookup_returns_core_users_and_active_users_only(
    db_session: Session,
    service: UserManagementService,
) -> None:
    active_user = create_test_user(db_session, "lookup-active")
    inactive_user = create_test_user(
        db_session,
        "lookup-inactive",
        is_active=False,
    )

    assert service.get_user(active_user.id) == active_user
    assert service.get_user(inactive_user.id) == inactive_user
    assert service.get_user(999) is None
    assert service.require_user(active_user.id) == active_user
    assert service.list_users() == [active_user, inactive_user]
    assert service.list_active_users() == [active_user]

    with pytest.raises(ValueError, match="User not found"):
        service.require_user(999)
