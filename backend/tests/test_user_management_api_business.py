from __future__ import annotations

from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.user_management.models import (
    UserManagementAuditEvent,
    UserManagementProfile,
    UserManagementRoleAssignment,
)


BASE_URL = "/api/v1/user-management"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="api-business-admin",
            full_name="API Business Admin",
            password_hash="not-used",
            role="test",
            is_active=True,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides = original_overrides


def create_user(
    db_session: Session,
    username: str = "user-management-api-user",
    *,
    is_active: bool = True,
) -> User:
    user = User(
        username=username,
        full_name="User Management API User",
        password_hash="not-used",
        role="test",
        is_active=is_active,
    )
    db_session.add(user)
    db_session.flush()
    return user


def create_profile(
    client: TestClient,
    user_id: int,
    *,
    display_name: str = "API Profile",
    personnel_number: str | None = "PN-API-001",
    job_title: str | None = "Operator",
    phone_number: str | None = "+380000000001",
    is_active: bool = True,
    notes: str | None = "Created through API business test",
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/profiles",
        json={
            "user_id": user_id,
            "display_name": display_name,
            "personnel_number": personnel_number,
            "job_title": job_title,
            "phone_number": phone_number,
            "is_active": is_active,
            "notes": notes,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_role_assignment(
    client: TestClient,
    user_id: int,
    *,
    role_code: str = "document.manager",
    scope_type: str | None = "department",
    scope_id: int | None = 10,
    is_active: bool = True,
    assigned_by_user_id: int | None = None,
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/role-assignments",
        json={
            "user_id": user_id,
            "role_code": role_code,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "is_active": is_active,
            "assigned_by_user_id": assigned_by_user_id,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_audit_event(
    client: TestClient,
    *,
    actor_user_id: int | None = None,
    target_user_id: int | None = None,
    event_type: str = "profile.created",
    summary: str | None = "Profile created",
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    response = client.post(
        f"{BASE_URL}/audit-events",
        json={
            "actor_user_id": actor_user_id,
            "target_user_id": target_user_id,
            "event_type": event_type,
            "summary": summary,
            "details": details,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_user_lookup_list_and_detail_endpoints_return_core_users(
    client: TestClient,
    db_session: Session,
) -> None:
    active_user = create_user(db_session, "api-lookup-active")
    inactive_user = create_user(db_session, "api-lookup-inactive", is_active=False)

    list_response = client.get(f"{BASE_URL}/users")
    detail_response = client.get(f"{BASE_URL}/users/{active_user.id}")
    inactive_detail_response = client.get(f"{BASE_URL}/users/{inactive_user.id}")

    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "id": active_user.id,
            "username": "api-lookup-active",
            "email": None,
            "is_active": True,
        },
        {
            "id": inactive_user.id,
            "username": "api-lookup-inactive",
            "email": None,
            "is_active": False,
        },
    ]
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == active_user.id
    assert inactive_detail_response.status_code == 200
    assert inactive_detail_response.json()["is_active"] is False


def test_user_detail_returns_not_found_for_unknown_user(client: TestClient) -> None:
    response = client.get(f"{BASE_URL}/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_users_list_exposes_exact_read_contract(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session, "api-contract-user")
    user.email = "contract@example.test"

    response = client.get(f"{BASE_URL}/users")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": user.id,
            "username": "api-contract-user",
            "email": "contract@example.test",
            "is_active": True,
        },
    ]


def test_users_list_requires_authentication() -> None:
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get(f"{BASE_URL}/users")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_profiles_list_exposes_exact_read_contract_with_nullable_fields(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session, "api-profile-contract-user")
    created = create_profile(
        client,
        user.id,
        display_name=None,
        personnel_number=None,
        job_title=None,
        phone_number=None,
        is_active=False,
        notes=None,
    )
    response = client.get(f"{BASE_URL}/profiles")
    assert response.status_code == 200
    assert response.json() == [created]
    assert set(created) == {
        "id", "user_id", "display_name", "personnel_number", "job_title",
        "phone_number", "is_active", "notes", "created_at", "updated_at",
    }
    for field in ("display_name", "personnel_number", "job_title", "phone_number", "notes"):
        assert created[field] is None
    datetime.fromisoformat(str(created["created_at"]).replace("Z", "+00:00"))
    datetime.fromisoformat(str(created["updated_at"]).replace("Z", "+00:00"))


def test_profiles_list_requires_authentication() -> None:
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get(f"{BASE_URL}/profiles")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_profile_create_update_read_list_and_database_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    created_profile = create_profile(client, user.id, display_name="Initial Name")

    assert isinstance(created_profile["id"], int)
    assert created_profile["user_id"] == user.id
    assert created_profile["display_name"] == "Initial Name"
    assert created_profile["personnel_number"] == "PN-API-001"
    assert created_profile["is_active"] is True
    assert isinstance(created_profile["created_at"], str)
    assert isinstance(created_profile["updated_at"], str)

    persisted_profile = db_session.get(UserManagementProfile, created_profile["id"])
    assert persisted_profile is not None
    assert persisted_profile.user_id == user.id
    assert persisted_profile.display_name == "Initial Name"

    update_response = client.patch(
        f"{BASE_URL}/profiles/{created_profile['id']}",
        json={
            "display_name": "Updated Name",
            "job_title": "Senior Operator",
            "is_active": False,
            "notes": "Updated through API",
        },
    )
    detail_response = client.get(f"{BASE_URL}/profiles/{created_profile['id']}")
    list_response = client.get(f"{BASE_URL}/profiles")

    assert update_response.status_code == 200
    updated_profile = update_response.json()
    assert updated_profile["id"] == created_profile["id"]
    assert updated_profile["display_name"] == "Updated Name"
    assert updated_profile["job_title"] == "Senior Operator"
    assert updated_profile["is_active"] is False
    assert updated_profile["notes"] == "Updated through API"
    assert detail_response.status_code == 200
    assert detail_response.json() == updated_profile
    assert list_response.status_code == 200
    assert list_response.json() == [updated_profile]

    db_session.refresh(persisted_profile)
    assert persisted_profile.display_name == "Updated Name"
    assert persisted_profile.is_active is False


def test_profile_endpoints_return_supported_validation_and_conflict_errors(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    create_profile(client, user.id)

    missing_user_response = client.post(
        f"{BASE_URL}/profiles",
        json={"user_id": 999, "display_name": "Missing User"},
    )
    duplicate_response = client.post(
        f"{BASE_URL}/profiles",
        json={"user_id": user.id, "display_name": "Duplicate"},
    )
    validation_response = client.post(
        f"{BASE_URL}/profiles",
        json={"display_name": "No User"},
    )
    not_found_response = client.get(f"{BASE_URL}/profiles/999")
    update_not_found_response = client.patch(
        f"{BASE_URL}/profiles/999",
        json={"display_name": "Missing"},
    )

    assert missing_user_response.status_code == 400
    assert missing_user_response.json() == {"detail": "User not found"}
    assert duplicate_response.status_code == 400
    assert duplicate_response.json() == {"detail": "User profile already exists"}
    assert validation_response.status_code == 422
    assert not_found_response.status_code == 404
    assert not_found_response.json() == {
        "detail": "User management profile not found",
    }
    assert update_not_found_response.status_code == 404
    assert update_not_found_response.json() == {
        "detail": "User management profile not found",
    }


def test_role_assignment_create_update_read_list_and_database_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session, "role-target")
    assigner = create_user(db_session, "role-assigner")
    created_assignment = create_role_assignment(
        client,
        user.id,
        assigned_by_user_id=assigner.id,
    )

    assert isinstance(created_assignment["id"], int)
    assert created_assignment["user_id"] == user.id
    assert created_assignment["role_code"] == "document.manager"
    assert created_assignment["scope_type"] == "department"
    assert created_assignment["scope_id"] == 10
    assert created_assignment["is_active"] is True
    assert created_assignment["assigned_by_user_id"] == assigner.id
    assert isinstance(created_assignment["assigned_at"], str)
    assert created_assignment["revoked_at"] is None

    persisted_assignment = db_session.get(
        UserManagementRoleAssignment,
        created_assignment["id"],
    )
    assert persisted_assignment is not None
    assert persisted_assignment.user_id == user.id
    assert persisted_assignment.role_code == "document.manager"

    update_response = client.patch(
        f"{BASE_URL}/role-assignments/{created_assignment['id']}",
        json={
            "role_code": "audit.reader",
            "scope_type": "project",
            "scope_id": 20,
            "is_active": False,
        },
    )
    detail_response = client.get(
        f"{BASE_URL}/role-assignments/{created_assignment['id']}",
    )
    list_response = client.get(f"{BASE_URL}/role-assignments")

    assert update_response.status_code == 200
    updated_assignment = update_response.json()
    assert updated_assignment["id"] == created_assignment["id"]
    assert updated_assignment["role_code"] == "audit.reader"
    assert updated_assignment["scope_type"] == "project"
    assert updated_assignment["scope_id"] == 20
    assert updated_assignment["is_active"] is False
    assert detail_response.status_code == 200
    assert detail_response.json() == updated_assignment
    assert list_response.status_code == 200
    assert list_response.json() == [updated_assignment]

    db_session.refresh(persisted_assignment)
    assert persisted_assignment.role_code == "audit.reader"
    assert persisted_assignment.is_active is False


def test_role_assignment_endpoints_return_supported_validation_and_conflict_errors(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)
    first_assignment = create_role_assignment(client, user.id)
    second_assignment = create_role_assignment(
        client,
        user.id,
        role_code="audit.reader",
    )

    missing_user_response = client.post(
        f"{BASE_URL}/role-assignments",
        json={"user_id": 999, "role_code": "document.manager"},
    )
    duplicate_create_response = client.post(
        f"{BASE_URL}/role-assignments",
        json={
            "user_id": user.id,
            "role_code": "document.manager",
            "scope_type": "department",
            "scope_id": 10,
        },
    )
    duplicate_update_response = client.patch(
        f"{BASE_URL}/role-assignments/{second_assignment['id']}",
        json={"role_code": first_assignment["role_code"]},
    )
    validation_response = client.post(
        f"{BASE_URL}/role-assignments",
        json={"user_id": user.id},
    )
    not_found_response = client.get(f"{BASE_URL}/role-assignments/999")
    update_not_found_response = client.patch(
        f"{BASE_URL}/role-assignments/999",
        json={"is_active": False},
    )

    assert missing_user_response.status_code == 400
    assert missing_user_response.json() == {"detail": "User not found"}
    assert duplicate_create_response.status_code == 400
    assert duplicate_create_response.json() == {
        "detail": "Active role assignment already exists",
    }
    assert duplicate_update_response.status_code == 400
    assert duplicate_update_response.json() == {
        "detail": "Active role assignment already exists",
    }
    assert validation_response.status_code == 422
    assert not_found_response.status_code == 404
    assert not_found_response.json() == {
        "detail": "User management role assignment not found",
    }
    assert update_not_found_response.status_code == 404
    assert update_not_found_response.json() == {
        "detail": "User management role assignment not found",
    }


def test_audit_event_create_read_list_and_database_persistence(
    client: TestClient,
    db_session: Session,
) -> None:
    actor = create_user(db_session, "audit-actor")
    target = create_user(db_session, "audit-target")
    first_event = create_audit_event(
        client,
        actor_user_id=actor.id,
        target_user_id=target.id,
        event_type="profile.created",
        summary="Profile created",
        details={"source": "api-business-test"},
    )
    second_event = create_audit_event(
        client,
        actor_user_id=actor.id,
        target_user_id=target.id,
        event_type="role.assigned",
        summary="Role assigned",
    )

    assert isinstance(first_event["id"], int)
    assert first_event["actor_user_id"] == actor.id
    assert first_event["target_user_id"] == target.id
    assert first_event["event_type"] == "profile.created"
    assert first_event["summary"] == "Profile created"
    assert first_event["details"] == {"source": "api-business-test"}
    assert isinstance(first_event["created_at"], str)

    persisted_event = db_session.get(UserManagementAuditEvent, first_event["id"])
    assert persisted_event is not None
    assert persisted_event.event_type == "profile.created"
    assert persisted_event.details == {"source": "api-business-test"}

    detail_response = client.get(f"{BASE_URL}/audit-events/{first_event['id']}")
    list_response = client.get(f"{BASE_URL}/audit-events")

    assert detail_response.status_code == 200
    assert detail_response.json() == first_event
    assert list_response.status_code == 200
    assert list_response.json() == [second_event, first_event]


def test_audit_event_endpoints_return_supported_validation_and_not_found_errors(
    client: TestClient,
    db_session: Session,
) -> None:
    actor = create_user(db_session)

    missing_actor_response = client.post(
        f"{BASE_URL}/audit-events",
        json={
            "actor_user_id": 999,
            "target_user_id": actor.id,
            "event_type": "profile.updated",
        },
    )
    missing_target_response = client.post(
        f"{BASE_URL}/audit-events",
        json={
            "actor_user_id": actor.id,
            "target_user_id": 999,
            "event_type": "profile.updated",
        },
    )
    validation_response = client.post(
        f"{BASE_URL}/audit-events",
        json={"actor_user_id": actor.id},
    )
    not_found_response = client.get(f"{BASE_URL}/audit-events/999")

    assert missing_actor_response.status_code == 400
    assert missing_actor_response.json() == {"detail": "User not found"}
    assert missing_target_response.status_code == 400
    assert missing_target_response.json() == {"detail": "User not found"}
    assert validation_response.status_code == 422
    assert not_found_response.status_code == 404
    assert not_found_response.json() == {
        "detail": "User management audit event not found",
    }
