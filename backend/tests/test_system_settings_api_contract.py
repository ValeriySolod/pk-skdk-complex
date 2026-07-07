"""API contract tests for the System Settings module."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.main import app
from app.modules.system_settings.models import (
    SystemSettingChangeAction,
    SystemSettingDefaultStatus,
    SystemSettingStatus,
    SystemSettingValueType,
)
from app.modules.system_settings.schemas import (
    SystemSettingChangeEventCreate,
    SystemSettingChangeEventListResponse,
    SystemSettingChangeEventRead,
    SystemSettingCreate,
    SystemSettingDefaultCreate,
    SystemSettingDefaultListResponse,
    SystemSettingDefaultRead,
    SystemSettingDefaultUpdate,
    SystemSettingListResponse,
    SystemSettingRead,
    SystemSettingUpdate,
    SystemSettingsHealthRead,
)


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Create an isolated in-memory database session for API contract tests."""

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    """Create a TestClient with database and authentication overrides."""

    def override_get_db() -> Iterator[Session]:
        yield db_session

    def override_get_current_user() -> object:
        return object()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _response_json(response: Any) -> dict[str, Any]:
    payload = response.json()
    assert isinstance(payload, dict)
    return payload


def test_system_settings_health_contract(client: TestClient) -> None:
    response = client.get("/api/v1/system-settings/health")

    assert response.status_code == 200
    payload = _response_json(response)

    assert payload["module"] == "system_settings"
    assert payload["status"] == "ok"
    assert payload["repositories"] == {
        "settings": True,
        "defaults": True,
        "change_events": True,
    }

    schema = SystemSettingsHealthRead.model_validate(payload)
    assert schema.module == "system_settings"
    assert schema.repositories == payload["repositories"]


def test_system_settings_openapi_contains_health_route(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = _response_json(response)

    path = payload["paths"]["/api/v1/system-settings/health"]["get"]
    assert path["tags"] == ["System Settings"]
    response_schema = path["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema["$ref"].endswith("/SystemSettingsHealthRead")


def test_system_setting_schemas_contract() -> None:
    create_payload = SystemSettingCreate.model_validate(
        {
            "category": "security",
            "key": "password_policy",
            "title": "Password Policy",
            "description": "Policy configuration",
            "value": {"min_length": 12},
            "default_value": {"min_length": 8},
            "value_type": "object",
            "validation_rules": {"required": ["min_length"]},
            "metadata_json": {"source": "contract-test"},
            "status": "active",
            "created_by_id": 1,
        }
    )

    assert create_payload.value_type == SystemSettingValueType.OBJECT
    assert create_payload.status == SystemSettingStatus.ACTIVE
    assert create_payload.metadata_json == {"source": "contract-test"}

    update_payload = SystemSettingUpdate.model_validate(
        {
            "value": {"min_length": 14},
            "status": "inactive",
            "updated_by_id": 2,
        }
    )
    assert update_payload.status == SystemSettingStatus.INACTIVE

    read_payload = SystemSettingRead.model_validate(
        {
            **create_payload.model_dump(),
            "id": 1,
            "uuid": "00000000-0000-4000-8000-000000000001",
            "updated_by_id": 2,
            "deleted_by_id": None,
            "created_at": "2026-07-07T10:00:00+00:00",
            "updated_at": "2026-07-07T10:01:00+00:00",
            "deleted_at": None,
        }
    )
    list_payload = SystemSettingListResponse(items=[read_payload], total=1, limit=10, offset=0)

    assert str(read_payload.uuid) == "00000000-0000-4000-8000-000000000001"
    assert list_payload.items[0].key == "password_policy"


def test_system_setting_default_schemas_contract() -> None:
    create_payload = SystemSettingDefaultCreate(
        category="ui",
        key="theme",
        title="Theme",
        default_value="light",
        value_type=SystemSettingValueType.STRING,
        validation_rules={"enum": ["light", "dark"]},
        status=SystemSettingDefaultStatus.ACTIVE,
        metadata_json={"source": "contract-test"},
    )

    update_payload = SystemSettingDefaultUpdate.model_validate(
        {"default_value": "dark", "status": "deprecated"}
    )
    assert update_payload.status == SystemSettingDefaultStatus.DEPRECATED

    read_payload = SystemSettingDefaultRead.model_validate(
        {
            **create_payload.model_dump(),
            "id": 1,
            "uuid": uuid4(),
            "description": None,
            "created_at": "2026-07-07T10:00:00+00:00",
            "updated_at": "2026-07-07T10:01:00+00:00",
        }
    )
    list_payload = SystemSettingDefaultListResponse(
        items=[read_payload], total=1, limit=10, offset=0
    )

    assert read_payload.key == "theme"
    assert list_payload.total == 1


def test_system_setting_change_event_schemas_contract() -> None:
    create_payload = SystemSettingChangeEventCreate.model_validate(
        {
            "system_setting_id": 1,
            "category": "security",
            "key": "password_policy",
            "action": "updated",
            "old_value": {"min_length": 12},
            "new_value": {"min_length": 14},
            "actor_user_id": 2,
            "reason": "Contract test",
            "source": "api",
            "request_id": "request-1",
            "correlation_id": "correlation-1",
            "metadata_json": {"source": "contract-test"},
        }
    )

    assert create_payload.action == SystemSettingChangeAction.UPDATED

    read_payload = SystemSettingChangeEventRead.model_validate(
        {
            **create_payload.model_dump(),
            "id": 1,
            "event_uuid": "00000000-0000-4000-8000-000000000003",
            "created_at": "2026-07-07T10:00:00+00:00",
        }
    )
    list_payload = SystemSettingChangeEventListResponse(
        items=[read_payload], total=1, limit=10, offset=0
    )

    assert str(read_payload.event_uuid) == "00000000-0000-4000-8000-000000000003"
    assert list_payload.items[0].new_value == {"min_length": 14}
