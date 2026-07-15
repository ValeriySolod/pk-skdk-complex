from __future__ import annotations

from collections import Counter
import os
from pathlib import Path
import subprocess
import sys

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, configure_mappers

from app.core.module_registry import registry
from app.core.security import get_current_user
from app.db.dependencies import get_db
from app.db.model_registration import register_models
from app.main import app
from app.models import Role, User


EXPECTED_MODULE_CODES = {
    "admin",
    "administration",
    "analytics",
    "audit-log",
    "backup-restore",
    "document-management",
    "file-storage",
    "integrations",
    "monitoring_health",
    "notifications",
    "organization-structure",
    "organizations",
    "registries",
    "reporting-analytics",
    "reports",
    "scanner",
    "search",
    "shipments",
    "system-settings",
    "user-management",
    "workflow",
}


def test_application_registers_each_expected_module_once() -> None:
    module_codes = [module["code"] for module in registry.list()]

    assert len(module_codes) == len(set(module_codes))
    assert set(module_codes) == EXPECTED_MODULE_CODES

    route_paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    for module_code in EXPECTED_MODULE_CODES:
        prefix = f"/api/v1/{module_code}"
        assert any(path == prefix or path.startswith(f"{prefix}/") for path in route_paths)


def test_application_route_path_and_method_combinations_are_unique() -> None:
    combinations = [
        (route.path, method)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
        if method not in {"HEAD", "OPTIONS"}
    ]

    assert [item for item, count in Counter(combinations).items() if count > 1] == []


def test_canonical_models_resolve_all_mappers_and_relationships() -> None:
    metadata = register_models()

    configure_mappers()

    assert len(metadata.tables) == 42
    foreign_key_targets = {
        foreign_key.target_fullname
        for table in metadata.tables.values()
        for foreign_key in table.foreign_keys
    }
    assert foreign_key_targets


def test_representative_module_health_requires_authentication(
    db_session: Session,
) -> None:
    client = TestClient(app)
    protected_path = "/api/v1/monitoring_health/health"

    assert client.get(protected_path).status_code == 401

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: User(
        username="readiness-user",
        full_name="Readiness User",
        password_hash="unused",
        role=Role.SYSTEM_ADMIN.value,
        is_active=True,
    )
    try:
        response = client.get(protected_path)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json() == {"module": "monitoring_health", "status": "ok"}


def test_startup_does_not_create_schema_and_clean_alembic_upgrade_reaches_head(
    tmp_path: Path,
) -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    database_path = tmp_path / "readiness-upgrade.db"
    database_url = f"sqlite+pysqlite:///{database_path.as_posix()}"
    environment = {**os.environ, "DATABASE_URL": database_url}

    startup_result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from app.main import app; "
                "from app.db.session import engine; "
                "from sqlalchemy import inspect; "
                "print(len(inspect(engine).get_table_names()))"
            ),
        ],
        cwd=backend_dir,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    assert startup_result.stdout.strip() == "0"

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=backend_dir,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        assert inspector.get_table_names() == sorted(
            ["alembic_version", *register_models().tables]
        )
        with engine.connect() as connection:
            assert connection.exec_driver_sql(
                "SELECT version_num FROM alembic_version"
            ).scalar_one() == "20260709_0013"
    finally:
        engine.dispose()
