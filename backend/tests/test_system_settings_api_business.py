"""API business tests for the System Settings module."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.models import User
from app.modules.system_settings.models import (
    SystemSettingStatus,
    SystemSettingValueType,
)

BASE_URL = "/api/v1/system-settings"


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    original_overrides = app.dependency_overrides.copy()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_current_user() -> User:
        return User(
            id=1,
            username="system-settings-api-business-admin",
            full_name="System Settings API Business Admin",
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


def setting_payload(
    key: str,
    *,
    category: str = "security",
    status: str = SystemSettingStatus.ACTIVE.value,
    value_type: str = SystemSettingValueType.STRING.value,
    value: object = "enabled",
) -> dict[str, object]:
    return {
        "category": category,
        "key": key,
        "title": f"Setting {key}",
        "description": "Business test setting",
        "value": value,
        "default_value": value,
        "value_type": value_type,
        "validation_rules": {"source": "business-test"},
        "metadata_json": {"source": "business-test"},
        "status": status,
        "created_by_id": None,
        "updated_by_id": None,
        "deleted_by_id": None,
    }


def test_health_route_returns_system_settings_repository_health(
    client: TestClient,
) -> None:
    response = client.get(f"{BASE_URL}/health")

    assert response.status_code == 200
    assert response.json() == {
        "module": "system_settings",
        "status": "ok",
        "repositories": {
            "settings": True,
            "defaults": True,
            "change_events": True,
        },
    }


def test_setting_routes_create_list_count_and_lookup_by_id_uuid_and_key(
    client: TestClient,
) -> None:
    first = client.post(
        f"{BASE_URL}/settings",
        json=setting_payload(
            "password_policy",
            category="security",
            value_type=SystemSettingValueType.OBJECT.value,
            value={"min_length": 12},
        ),
    )
    second = client.post(
        f"{BASE_URL}/settings",
        json=setting_payload("theme", category="ui", value="dark"),
    )

    assert first.status_code == 201
    assert second.status_code == 201
    setting = first.json()
    assert setting["category"] == "security"
    assert setting["key"] == "password_policy"
    assert setting["value"] == {"min_length": 12}
    assert setting["uuid"]

    listed = client.get(f"{BASE_URL}/settings", params={"limit": 1, "offset": 0})
    assert listed.status_code == 200
    assert listed.json()["total"] == 2
    assert listed.json()["limit"] == 1
    assert len(listed.json()["items"]) == 1

    counted = client.get(f"{BASE_URL}/settings/count")
    assert counted.status_code == 200
    assert counted.json() == {"total": 2}

    by_id = client.get(f"{BASE_URL}/settings/{setting['id']}")
    by_uuid = client.get(f"{BASE_URL}/settings/uuid/{setting['uuid']}")
    by_key = client.get(f"{BASE_URL}/settings/key/security/password_policy")
    assert by_id.status_code == 200
    assert by_uuid.status_code == 200
    assert by_key.status_code == 200
    assert by_id.json() == by_uuid.json() == by_key.json() == setting


def test_setting_filters_return_only_matching_records(client: TestClient) -> None:
    active_security = client.post(
        f"{BASE_URL}/settings",
        json=setting_payload(
            "password_policy",
            category="security",
            status=SystemSettingStatus.ACTIVE.value,
            value_type=SystemSettingValueType.OBJECT.value,
            value={"min_length": 12},
        ),
    ).json()
    client.post(
        f"{BASE_URL}/settings",
        json=setting_payload(
            "login_banner",
            category="security",
            status=SystemSettingStatus.INACTIVE.value,
        ),
    )
    client.post(
        f"{BASE_URL}/settings",
        json=setting_payload(
            "email_enabled",
            category="notifications",
            value_type=SystemSettingValueType.BOOLEAN.value,
            value=True,
        ),
    )

    filtered = client.get(
        f"{BASE_URL}/settings",
        params={
            "category": "security",
            "status": SystemSettingStatus.ACTIVE.value,
            "value_type": SystemSettingValueType.OBJECT.value,
        },
    )

    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert [item["id"] for item in filtered.json()["items"]] == [
        active_security["id"]
    ]
    assert client.get(
        f"{BASE_URL}/settings/count",
        params={"category": "notifications"},
    ).json() == {"total": 1}


def test_setting_update_persists_mutable_fields_and_preserves_identity(
    client: TestClient,
) -> None:
    created = client.post(
        f"{BASE_URL}/settings",
        json=setting_payload("session_timeout", value=15),
    ).json()

    response = client.patch(
        f"{BASE_URL}/settings/{created['id']}",
        json={
            "id": 999,
            "uuid": "00000000-0000-4000-8000-000000000999",
            "title": "Updated Session Timeout",
            "value": 30,
            "value_type": SystemSettingValueType.INTEGER.value,
            "status": SystemSettingStatus.INACTIVE.value,
            "metadata_json": {"updated": True},
        },
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == created["id"]
    assert updated["uuid"] == created["uuid"]
    assert updated["key"] == "session_timeout"
    assert updated["title"] == "Updated Session Timeout"
    assert updated["value"] == 30
    assert updated["value_type"] == SystemSettingValueType.INTEGER.value
    assert updated["status"] == SystemSettingStatus.INACTIVE.value
    assert updated["metadata_json"] == {"updated": True}
    assert client.get(f"{BASE_URL}/settings/{created['id']}").json() == updated


def test_setting_delete_excludes_from_normal_lists_and_lookup(
    client: TestClient,
) -> None:
    setting = client.post(
        f"{BASE_URL}/settings",
        json=setting_payload("obsolete_flag"),
    ).json()

    deleted = client.delete(f"{BASE_URL}/settings/{setting['id']}")

    assert deleted.status_code == 204
    assert client.get(f"{BASE_URL}/settings/{setting['id']}").status_code == 404
    assert client.get(f"{BASE_URL}/settings").json()["total"] == 0

    with_deleted = client.get(
        f"{BASE_URL}/settings",
        params={"include_deleted": True},
    )
    assert with_deleted.status_code == 200
    assert with_deleted.json()["total"] == 1
    assert with_deleted.json()["items"][0]["deleted_at"] is not None


def test_setting_error_behaviors_for_missing_invalid_and_duplicate_records(
    client: TestClient,
) -> None:
    assert client.get(f"{BASE_URL}/settings/999").status_code == 404
    missing_update = client.patch(
        f"{BASE_URL}/settings/999",
        json={"title": "Missing"},
    )
    assert missing_update.status_code == 404
    assert client.delete(f"{BASE_URL}/settings/999").status_code == 404

    invalid = client.post(
        f"{BASE_URL}/settings",
        json={**setting_payload(""), "title": "", "category": ""},
    )
    assert invalid.status_code == 422

    duplicate_payload = setting_payload("duplicate_key", category="security")
    created = client.post(f"{BASE_URL}/settings", json=duplicate_payload)
    assert created.status_code == 201

    duplicate = client.post(f"{BASE_URL}/settings", json=duplicate_payload)
    assert duplicate.status_code == 409
