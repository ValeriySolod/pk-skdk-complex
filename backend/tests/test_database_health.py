from __future__ import annotations

from collections.abc import Generator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.health import router as health_router
from app.db.dependencies import get_db
from app.services.database import DatabaseHealthService


class HealthySession:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def execute(self, statement: object) -> None:
        self.statements.append(str(statement))


class FailingSession:
    def execute(self, statement: object) -> None:
        raise SQLAlchemyError("connection failed")


def create_client(session: object) -> TestClient:
    app = FastAPI()
    app.include_router(health_router)

    def override_get_db() -> Generator[object, None, None]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_database_health_service_reports_connected_database() -> None:
    session = HealthySession()

    result = DatabaseHealthService(session).check_connection()

    assert result.is_healthy is True
    assert result.database == "connected"
    assert result.as_response() == {"status": "ok", "database": "connected"}
    assert session.statements == ["SELECT 1"]


def test_database_health_service_reports_disconnected_database() -> None:
    result = DatabaseHealthService(FailingSession()).check_connection()

    assert result.is_healthy is False
    assert result.database == "disconnected"
    assert result.as_response() == {
        "status": "unhealthy",
        "database": "disconnected",
        "detail": "Database connection check failed",
    }


def test_database_health_endpoint_returns_healthy_response() -> None:
    client = create_client(HealthySession())

    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_database_health_endpoint_returns_unhealthy_response() -> None:
    client = create_client(FailingSession())

    response = client.get("/health/database")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unhealthy",
        "database": "disconnected",
        "detail": "Database connection check failed",
    }
