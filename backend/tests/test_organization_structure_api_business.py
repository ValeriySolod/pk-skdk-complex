from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User


BASE_URL = "/api/v1/organization-structure"


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


def create_unit(
    client: TestClient,
    *,
    name: str = "Head Office",
    code: str | None = "HEAD",
    parent_id: int | None = None,
    is_active: bool = True,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": name,
        "is_active": is_active,
    }
    if code is not None:
        payload["code"] = code
    if parent_id is not None:
        payload["parent_id"] = parent_id

    response = client.post(f"{BASE_URL}/units", json=payload)

    assert response.status_code == 201
    return response.json()


def test_create_root_unit_returns_business_fields_and_can_be_fetched(
    client: TestClient,
) -> None:
    created_unit = create_unit(client, name="Operations", code="OPS")

    assert isinstance(created_unit["id"], int)
    assert created_unit["name"] == "Operations"
    assert created_unit["code"] == "OPS"
    assert created_unit["parent_id"] is None
    assert created_unit["is_active"] is True

    detail_response = client.get(f"{BASE_URL}/units/{created_unit['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json() == created_unit


def test_create_child_unit_preserves_parent_id_and_list_relation(
    client: TestClient,
) -> None:
    parent_unit = create_unit(client, name="Head Office", code="HEAD")
    child_unit = create_unit(
        client,
        name="Field Team",
        code="FIELD",
        parent_id=int(parent_unit["id"]),
    )

    detail_response = client.get(f"{BASE_URL}/units/{child_unit['id']}")
    list_response = client.get(f"{BASE_URL}/units")

    assert detail_response.status_code == 200
    assert detail_response.json()["parent_id"] == parent_unit["id"]
    assert list_response.status_code == 200
    assert list_response.json() == [parent_unit, child_unit]


def test_update_unit_persists_changes_and_deactivation_hides_from_active_reads(
    client: TestClient,
) -> None:
    created_unit = create_unit(client, name="Registry", code="REG")

    update_response = client.patch(
        f"{BASE_URL}/units/{created_unit['id']}",
        json={
            "name": "Registry Archive",
            "code": "REG-ARCH",
            "is_active": False,
        },
    )

    assert update_response.status_code == 200
    updated_unit = update_response.json()
    assert updated_unit["id"] == created_unit["id"]
    assert updated_unit["name"] == "Registry Archive"
    assert updated_unit["code"] == "REG-ARCH"
    assert updated_unit["parent_id"] is None
    assert updated_unit["is_active"] is False

    detail_response = client.get(f"{BASE_URL}/units/{created_unit['id']}")
    list_response = client.get(f"{BASE_URL}/units")

    assert detail_response.status_code == 404
    assert detail_response.json() == {"detail": "Organization unit not found"}
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_unknown_unit_reads_and_updates_return_not_found(client: TestClient) -> None:
    get_response = client.get(f"{BASE_URL}/units/999")
    update_response = client.patch(
        f"{BASE_URL}/units/999",
        json={"name": "Missing Unit"},
    )

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Organization unit not found"}
    assert update_response.status_code == 404
    assert update_response.json() == {"detail": "Organization unit not found"}


def test_create_unit_requires_name(client: TestClient) -> None:
    response = client.post(f"{BASE_URL}/units", json={"code": "NO-NAME"})

    assert response.status_code == 422


def test_create_unit_rejects_invalid_payload_types(client: TestClient) -> None:
    response = client.post(
        f"{BASE_URL}/units",
        json={"name": "Operations", "parent_id": "invalid-parent"},
    )

    assert response.status_code == 422


def test_create_unit_rejects_missing_parent_with_bad_request(
    client: TestClient,
) -> None:
    response = client.post(
        f"{BASE_URL}/units",
        json={
            "name": "Field Team",
            "code": "FIELD",
            "parent_id": 999,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Organization unit not found"}


def test_update_unit_rejects_duplicate_code_with_bad_request(
    client: TestClient,
) -> None:
    create_unit(client, name="Head Office", code="HEAD")
    branch_unit = create_unit(client, name="Branch Office", code="BRANCH")

    response = client.patch(
        f"{BASE_URL}/units/{branch_unit['id']}",
        json={"code": "HEAD"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Organization unit code already exists"}
