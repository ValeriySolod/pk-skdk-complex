from __future__ import annotations

from collections.abc import Generator
import json
from pathlib import Path
import subprocess
import sys
from threading import Event, Thread

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Column, Integer, MetaData, String, Table, select
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.db import dependencies
from app.db.session import SessionLocal, create_database_engine, engine


EXPECTED_TABLES = {
    "administration_action_events",
    "administration_maintenance_tasks",
    "administration_references",
    "analytics_dashboard_definitions",
    "analytics_report_definitions",
    "analytics_report_runs",
    "analytics_snapshots",
    "audit_log_events",
    "audit_logs",
    "backup_jobs",
    "contracts",
    "document_audit_events",
    "document_categories",
    "document_permissions",
    "document_tag_assignments",
    "document_tags",
    "document_versions",
    "documents",
    "employee_assignments",
    "file_storage_objects",
    "health_check_records",
    "integration_connections",
    "integration_events",
    "integration_providers",
    "integration_sync_jobs",
    "monitoring_metrics",
    "notification_deliveries",
    "notifications",
    "organization_units",
    "organizations",
    "positions",
    "registries",
    "restore_jobs",
    "shipments",
    "system_incidents",
    "system_setting_change_events",
    "system_setting_defaults",
    "system_settings",
    "user_management_audit_events",
    "user_management_profiles",
    "user_management_role_assignments",
    "users",
}


class TrackingSession:
    def __init__(self) -> None:
        self.closed = False
        self.rolled_back = False

    def close(self) -> None:
        self.closed = True

    def rollback(self) -> None:
        self.rolled_back = True


def consume_dependency(
    generator: Generator[TrackingSession, None, None],
) -> TrackingSession:
    session = next(generator)
    with pytest.raises(StopIteration):
        next(generator)
    return session


def test_database_dependency_yields_and_closes_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = TrackingSession()
    monkeypatch.setattr(dependencies, "SessionLocal", lambda: session)

    yielded_session = consume_dependency(dependencies.get_db())

    assert yielded_session is session
    assert session.rolled_back is False
    assert session.closed is True


def test_database_dependency_rolls_back_and_closes_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = TrackingSession()
    expected_error = RuntimeError("transaction failed")
    monkeypatch.setattr(dependencies, "SessionLocal", lambda: session)
    generator = dependencies.get_db()

    assert next(generator) is session
    with pytest.raises(RuntimeError) as error:
        generator.throw(expected_error)

    assert error.value is expected_error
    assert session.rolled_back is True
    assert session.closed is True


def test_metadata_registers_every_completed_module_table() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    alembic_env_script = """
import json
import runpy
from contextlib import nullcontext
from pathlib import Path

from alembic import context
from app.db import Base

captured = {}

class TestConfig:
    config_file_name = None

context.config = TestConfig()
context.is_offline_mode = lambda: True
context.configure = lambda **kwargs: captured.update(kwargs)
context.begin_transaction = nullcontext
context.run_migrations = lambda: None

runpy.run_path(Path("alembic") / "env.py", run_name="alembic_env_under_test")
target_metadata = captured["target_metadata"]
print(json.dumps({
    "is_base_metadata": target_metadata is Base.metadata,
    "tables": sorted(target_metadata.tables),
}))
"""
    result = subprocess.run(
        [sys.executable, "-c", alembic_env_script],
        cwd=backend_dir,
        check=True,
        capture_output=True,
        text=True,
    )

    registration = json.loads(result.stdout)
    assert registration["is_base_metadata"] is True
    assert set(registration["tables"]) == EXPECTED_TABLES


def test_application_in_memory_sqlite_is_shared_between_threads() -> None:
    metadata = MetaData()
    records = Table(
        "thread_sharing_regression",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("value", String(80), nullable=False),
    )
    schema_ready = Event()
    reader_finished = Event()
    errors: list[BaseException] = []
    observed_rows: list[tuple[int, str]] = []

    def create_schema_and_data() -> None:
        try:
            metadata.create_all(engine)
            with SessionLocal() as session:
                session.execute(records.insert().values(id=1, value="shared"))
                session.commit()
            schema_ready.set()
            reader_finished.wait(timeout=5)
        except BaseException as error:
            errors.append(error)
            schema_ready.set()

    def read_schema_and_data() -> None:
        schema_ready.wait(timeout=5)
        try:
            with SessionLocal() as session:
                observed_rows.extend(session.execute(select(records)).all())
        except BaseException as error:
            errors.append(error)
        finally:
            reader_finished.set()

    creator = Thread(target=create_schema_and_data)
    reader = Thread(target=read_schema_and_data)
    creator.start()
    reader.start()
    creator.join(timeout=5)
    reader.join(timeout=5)

    assert errors == []
    assert observed_rows == [(1, "shared")]


@pytest.mark.parametrize(
    "database_url",
    ("sqlite://", "sqlite:///:memory:", "sqlite+pysqlite://", "sqlite+pysqlite:///:memory:"),
)
def test_in_memory_sqlite_engine_uses_static_pool(database_url: str) -> None:
    configured_engine = create_database_engine(database_url)
    try:
        assert isinstance(configured_engine.pool, StaticPool)
    finally:
        configured_engine.dispose()


def test_file_backed_sqlite_engine_does_not_use_static_pool(tmp_path: Path) -> None:
    configured_engine = create_database_engine(
        f"sqlite+pysqlite:///{tmp_path / 'application.db'}"
    )
    try:
        assert not isinstance(configured_engine.pool, StaticPool)
    finally:
        configured_engine.dispose()


def test_model_indexes_match_existing_migration_schema() -> None:
    expected_indexes = {
        "documents": {("ix_documents_document_number", ("document_number",), False), ("ix_documents_document_type", ("document_type",), False), ("ix_documents_organization_id", ("organization_id",), False), ("ix_documents_owner_user_id", ("owner_user_id",), False), ("ix_documents_status", ("status",), False), ("ix_documents_title", ("title",), False)},
        "document_categories": {("ix_document_categories_code", ("code",), False), ("ix_document_categories_is_active", ("is_active",), False), ("ix_document_categories_name", ("name",), False)},
        "document_tags": {("ix_document_tags_name", ("name",), False)},
        "document_versions": {("ix_document_versions_document_id", ("document_id",), False), ("ix_document_versions_uploaded_at", ("uploaded_at",), False), ("ix_document_versions_uploaded_by", ("uploaded_by",), False), ("ix_document_versions_version", ("version",), False)},
        "document_tag_assignments": {("ix_document_tag_assignments_document_id", ("document_id",), False), ("ix_document_tag_assignments_tag_id", ("tag_id",), False)},
        "document_permissions": {("ix_document_permissions_document_id", ("document_id",), False), ("ix_document_permissions_permission", ("permission",), False), ("ix_document_permissions_principal_id", ("principal_id",), False), ("ix_document_permissions_principal_type", ("principal_type",), False)},
        "document_audit_events": {("ix_document_audit_events_action", ("action",), False), ("ix_document_audit_events_created_at", ("created_at",), False), ("ix_document_audit_events_document_id", ("document_id",), False), ("ix_document_audit_events_user_id", ("user_id",), False)},
        "user_management_profiles": {("ix_user_management_profiles_is_active", ("is_active",), False), ("ix_user_management_profiles_personnel_number", ("personnel_number",), False), ("ix_user_management_profiles_user_id", ("user_id",), False)},
        "user_management_role_assignments": {("ix_user_management_role_assignments_is_active", ("is_active",), False), ("ix_user_management_role_assignments_role_code", ("role_code",), False), ("ix_user_management_role_assignments_scope_id", ("scope_id",), False), ("ix_user_management_role_assignments_scope_type", ("scope_type",), False), ("ix_user_management_role_assignments_user_id", ("user_id",), False)},
        "user_management_audit_events": {("ix_user_management_audit_events_actor_user_id", ("actor_user_id",), False), ("ix_user_management_audit_events_created_at", ("created_at",), False), ("ix_user_management_audit_events_event_type", ("event_type",), False), ("ix_user_management_audit_events_target_user_id", ("target_user_id",), False)},
    }

    for table_name, expected in expected_indexes.items():
        actual = {
            (index.name, tuple(column.name for column in index.columns), bool(index.unique))
            for index in Base.metadata.tables[table_name].indexes
        }
        assert actual == expected


def test_alembic_revisions_form_one_continuous_chain() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    script = ScriptDirectory.from_config(config)
    revisions = list(script.walk_revisions(base="base", head="heads"))

    assert script.get_heads() == ["20260709_0013"]
    assert len(revisions) == 13
    for current, parent in zip(revisions, revisions[1:]):
        assert current.down_revision == parent.revision
    assert revisions[-1].down_revision is None
    assert all(callable(revision.module.upgrade) for revision in revisions)
    assert all(callable(revision.module.downgrade) for revision in revisions)
