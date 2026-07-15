"""API contract tests for the Administration module routes."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.modules.administration.schemas import (
    AdminActionEventCreate,
    AdminActionEventRead,
    AdministrationHealthRead,
    AdministrationReferenceCreate,
    AdministrationReferenceRead,
    AdministrationReferenceUpdate,
    MaintenanceTaskCreate,
    MaintenanceTaskRead,
    MaintenanceTaskUpdate,
)


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Create an isolated in-memory database session for API contract tests."""

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    """Create a TestClient with database dependency override."""

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _response_json(response: Any) -> dict[str, Any]:
    payload = response.json()
    assert isinstance(payload, dict)
    return payload


def test_administration_health_contract(client: TestClient) -> None:
    response = client.get("/api/v1/administration/health")

    assert response.status_code == 200
    payload = _response_json(response)

    assert "status" in payload
    assert isinstance(payload["status"], str)


def test_administration_health_schema_accepts_route_payload(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/administration/health")

    assert response.status_code == 200

    schema = AdministrationHealthRead.model_validate(response.json())

    assert isinstance(schema.status, str)


def test_administration_openapi_contains_health_route(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = _response_json(response)

    assert "/api/v1/administration/health" in payload["paths"]
    assert "get" in payload["paths"]["/api/v1/administration/health"]


def test_administration_reference_create_schema_contract() -> None:
    schema = AdministrationReferenceCreate.model_validate(
        {
            "catalog": "system",
            "code": "sample-reference",
            "title": "Sample Reference",
            "description": "Contract test reference",
            "status": "active",
            "metadata_json": {"source": "contract-test"},
        }
    )

    assert schema.catalog == "system"
    assert schema.code == "sample-reference"
    assert schema.title == "Sample Reference"
    assert schema.description == "Contract test reference"
    assert schema.status == "active"
    assert schema.metadata_json == {"source": "contract-test"}


def test_administration_reference_update_schema_contract() -> None:
    schema = AdministrationReferenceUpdate.model_validate(
        {
            "title": "Updated Reference",
            "status": "inactive",
            "metadata_json": {"updated": True},
        }
    )

    assert schema.title == "Updated Reference"
    assert schema.status == "inactive"
    assert schema.metadata_json == {"updated": True}


def test_administration_reference_read_schema_contract() -> None:
    schema = AdministrationReferenceRead.model_validate(
        {
            "id": 1,
            "uuid": "00000000-0000-4000-8000-000000000001",
            "catalog": "system",
            "code": "sample-reference",
            "title": "Sample Reference",
            "description": None,
            "status": "active",
            "metadata_json": None,
            "created_at": "2026-07-07T10:00:00+00:00",
            "updated_at": None,
            "deleted_at": None,
        }
    )

    assert schema.id == 1
    assert str(schema.uuid) == "00000000-0000-4000-8000-000000000001"
    assert schema.catalog == "system"


def test_maintenance_task_create_schema_contract() -> None:
    schema = MaintenanceTaskCreate.model_validate(
        {
            "code": "maintenance-contract",
            "title": "Maintenance Contract",
            "description": "Contract test maintenance task",
            "status": "pending",
            "priority": "normal",
            "metadata_json": {"source": "contract-test"},
        }
    )

    assert schema.code == "maintenance-contract"
    assert schema.title == "Maintenance Contract"
    assert schema.status == "pending"
    assert schema.priority == "normal"
    assert schema.metadata_json == {"source": "contract-test"}


def test_maintenance_task_update_schema_contract() -> None:
    schema = MaintenanceTaskUpdate.model_validate(
        {
            "status": "completed",
            "priority": "high",
            "metadata_json": {"updated": True},
        }
    )

    assert schema.status == "completed"
    assert schema.priority == "high"
    assert schema.metadata_json == {"updated": True}


def test_maintenance_task_read_schema_contract() -> None:
    schema = MaintenanceTaskRead.model_validate(
        {
            "id": 1,
            "uuid": "00000000-0000-4000-8000-000000000002",
            "code": "maintenance-contract",
            "title": "Maintenance Contract",
            "description": None,
            "status": "pending",
            "priority": "normal",
            "scheduled_for": None,
            "completed_at": None,
            "metadata_json": None,
            "created_at": "2026-07-07T10:00:00+00:00",
            "updated_at": None,
            "deleted_at": None,
        }
    )

    assert schema.id == 1
    assert str(schema.uuid) == "00000000-0000-4000-8000-000000000002"
    assert schema.code == "maintenance-contract"


def test_admin_action_event_create_schema_contract() -> None:
    schema = AdminActionEventCreate.model_validate(
        {
            "actor_user_id": None,
            "action": "contract.created",
            "target_type": "administration_reference",
            "target_id": "sample-reference",
            "description": "Contract test action event",
            "metadata_json": {"source": "contract-test"},
        }
    )

    assert schema.actor_user_id is None
    assert schema.action == "contract.created"
    assert schema.target_type == "administration_reference"
    assert schema.target_id == "sample-reference"
    assert schema.metadata_json == {"source": "contract-test"}


def test_admin_action_event_read_schema_contract() -> None:
    schema = AdminActionEventRead.model_validate(
        {
            "id": 1,
            "uuid": "00000000-0000-4000-8000-000000000003",
            "actor_user_id": None,
            "action": "contract.created",
            "target_type": "administration_reference",
            "target_id": "sample-reference",
            "description": None,
            "metadata_json": None,
            "created_at": "2026-07-07T10:00:00+00:00",
        }
    )

    assert schema.id == 1
    assert str(schema.uuid) == "00000000-0000-4000-8000-000000000003"
    assert schema.action == "contract.created"
