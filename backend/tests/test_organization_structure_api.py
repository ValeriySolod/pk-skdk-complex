from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="test-admin",
            full_name="Test Admin",
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


def test_organization_structure_routes_are_registered() -> None:
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}

    assert "/api/v1/organization-structure/health" in paths
    assert "/api/v1/organization-structure/units" in paths
    assert "/api/v1/organization-structure/units/{unit_id}" in paths
    assert "/api/v1/organization-structure/positions" in paths
    assert "/api/v1/organization-structure/positions/{position_id}" in paths
    assert "/api/v1/organization-structure/assignments" in paths
    assert "/api/v1/organization-structure/assignments/{assignment_id}" in paths


def test_organization_structure_health_route_is_reachable(client: TestClient) -> None:
    response = client.get("/api/v1/organization-structure/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_organization_unit_create_list_read_update_flow(client: TestClient) -> None:
    list_response = client.get("/api/v1/organization-structure/units")

    assert list_response.status_code == 200
    assert list_response.json() == []

    create_response = client.post(
        "/api/v1/organization-structure/units",
        json={"name": "Operations", "code": "OPS"},
    )

    assert create_response.status_code == 201
    created_unit = create_response.json()
    assert created_unit["id"] == 1
    assert created_unit["name"] == "Operations"
    assert created_unit["code"] == "OPS"
    assert created_unit["parent_id"] is None
    assert created_unit["is_active"] is True

    detail_response = client.get(
        f"/api/v1/organization-structure/units/{created_unit['id']}",
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == created_unit

    update_response = client.patch(
        f"/api/v1/organization-structure/units/{created_unit['id']}",
        json={"name": "Operations Updated", "is_active": False},
    )

    assert update_response.status_code == 200
    updated_unit = update_response.json()
    assert updated_unit["id"] == created_unit["id"]
    assert updated_unit["name"] == "Operations Updated"
    assert updated_unit["code"] == "OPS"
    assert updated_unit["is_active"] is False


def test_organization_units_list_exposes_exact_read_contract(client: TestClient) -> None:
    client.post(
        "/api/v1/organization-structure/units",
        json={"name": "Operations", "code": "OPS"},
    )

    response = client.get("/api/v1/organization-structure/units")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Operations",
            "code": "OPS",
            "parent_id": None,
            "is_active": True,
        },
    ]


def test_organization_units_list_requires_authentication() -> None:
    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get(
            "/api/v1/organization-structure/units",
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_position_create_list_read_update_flow(client: TestClient) -> None:
    unit_response = client.post(
        "/api/v1/organization-structure/units",
        json={"name": "Security", "code": "SEC"},
    )
    unit_id = unit_response.json()["id"]

    list_response = client.get("/api/v1/organization-structure/positions")

    assert list_response.status_code == 200
    assert list_response.json() == []

    create_response = client.post(
        "/api/v1/organization-structure/positions",
        json={
            "title": "Inspector",
            "code": "INSP",
            "organization_unit_id": unit_id,
        },
    )

    assert create_response.status_code == 201
    created_position = create_response.json()
    assert created_position["id"] == 1
    assert created_position["title"] == "Inspector"
    assert created_position["code"] == "INSP"
    assert created_position["organization_unit_id"] == unit_id
    assert created_position["is_active"] is True

    detail_response = client.get(
        f"/api/v1/organization-structure/positions/{created_position['id']}",
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == created_position

    update_response = client.patch(
        f"/api/v1/organization-structure/positions/{created_position['id']}",
        json={"title": "Senior Inspector", "is_active": False},
    )

    assert update_response.status_code == 200
    updated_position = update_response.json()
    assert updated_position["id"] == created_position["id"]
    assert updated_position["title"] == "Senior Inspector"
    assert updated_position["code"] == "INSP"
    assert updated_position["organization_unit_id"] == unit_id
    assert updated_position["is_active"] is False


def test_employee_assignment_create_list_read_update_flow(client: TestClient) -> None:
    unit_response = client.post(
        "/api/v1/organization-structure/units",
        json={"name": "Registry", "code": "REG"},
    )
    position_response = client.post(
        "/api/v1/organization-structure/positions",
        json={
            "title": "Registrar",
            "code": "REG-1",
            "organization_unit_id": unit_response.json()["id"],
        },
    )

    list_response = client.get("/api/v1/organization-structure/assignments")

    assert list_response.status_code == 200
    assert list_response.json() == []

    create_response = client.post(
        "/api/v1/organization-structure/assignments",
        json={
            "user_id": 1,
            "position_id": position_response.json()["id"],
            "start_date": "2026-01-01",
        },
    )

    assert create_response.status_code == 201
    created_assignment = create_response.json()
    assert created_assignment["id"] == 1
    assert created_assignment["user_id"] == 1
    assert created_assignment["position_id"] == position_response.json()["id"]
    assert created_assignment["start_date"] == "2026-01-01"
    assert created_assignment["end_date"] is None
    assert created_assignment["is_active"] is True

    detail_response = client.get(
        f"/api/v1/organization-structure/assignments/{created_assignment['id']}",
    )

    assert detail_response.status_code == 200
    assert detail_response.json() == created_assignment

    update_response = client.patch(
        f"/api/v1/organization-structure/assignments/{created_assignment['id']}",
        json={"end_date": "2026-12-31", "is_active": False},
    )

    assert update_response.status_code == 200
    updated_assignment = update_response.json()
    assert updated_assignment["id"] == created_assignment["id"]
    assert updated_assignment["end_date"] == "2026-12-31"
    assert updated_assignment["is_active"] is False


def test_organization_structure_detail_routes_return_not_found_for_unknown_ids(
    client: TestClient,
) -> None:
    expected_responses = (
        ("/api/v1/organization-structure/units/999", "Organization unit not found"),
        ("/api/v1/organization-structure/positions/999", "Position not found"),
        (
            "/api/v1/organization-structure/assignments/999",
            "Employee assignment not found",
        ),
    )

    for path, detail in expected_responses:
        response = client.get(path)

        assert response.status_code == 404
        assert response.json() == {"detail": detail}
