from __future__ import annotations

from collections.abc import Callable
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest
from alembic.config import Config
from sqlalchemy.engine import make_url

from app import postgres_release_validation as validation


class FakeEngine:
    def __init__(self) -> None:
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


@pytest.mark.parametrize("value", (None, ""))
def test_validation_url_is_required(value: str | None) -> None:
    with pytest.raises(validation.ReleaseValidationError, match="must be explicitly set"):
        validation.require_safe_validation_url(value)


@pytest.mark.parametrize(
    "value",
    ("sqlite:///validation.db", "mysql://user:pass@localhost/skdk_validation"),
)
def test_validation_url_must_be_postgresql(value: str) -> None:
    with pytest.raises(validation.ReleaseValidationError, match="requires a PostgreSQL URL"):
        validation.require_safe_validation_url(value)


@pytest.mark.parametrize(
    "database_name",
    ("skdk", "skdk_development", "postgres", "production", "special"),
)
def test_validation_database_name_must_be_clearly_disposable(database_name: str) -> None:
    with pytest.raises(validation.ReleaseValidationError, match="disposable/test-only marker"):
        validation.require_safe_validation_url(
            f"postgresql+psycopg://user:password@localhost/{database_name}"
        )


def test_validation_url_accepts_explicit_test_database() -> None:
    url = validation.require_safe_validation_url(
        "postgresql+psycopg://user:password@localhost/skdk_release_validation"
    )

    assert url.database == "skdk_release_validation"


def test_alembic_config_uses_dedicated_programmatic_url_override() -> None:
    url = make_url(
        "postgresql+psycopg://user:p%25ss@localhost/skdk_release_validation"
    )

    config = validation.build_alembic_config(url)

    assert config.attributes[validation.ALEMBIC_VALIDATION_URL_ATTRIBUTE] is url
    assert config.get_main_option("sqlalchemy.url") == ""
    assert config.attributes[validation.ALEMBIC_VALIDATION_URL_ATTRIBUTE].password == "p%ss"


def _read_alembic_environment_url(*, use_override: bool) -> str:
    backend_dir = Path(__file__).resolve().parents[1]
    script = f"""
import json
import runpy
from contextlib import nullcontext
from pathlib import Path

from alembic import context
from alembic.config import Config
from sqlalchemy import make_url
import sqlalchemy

class Connection:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None

class Engine:
    def connect(self):
        return Connection()

def engine_from_config(configuration, **kwargs):
    print(str(configuration["sqlalchemy.url"]))
    return Engine()

sqlalchemy.engine_from_config = engine_from_config

config = Config()
config.config_file_name = None
config.set_main_option("sqlalchemy.url", "sqlite:///ini_should_not_be_used.db")
if {use_override!r}:
    config.attributes["postgres_release_validation_database_url"] = make_url("sqlite:///validator.db")
context.config = config
context.is_offline_mode = lambda: False
context.configure = lambda **kwargs: None
context.begin_transaction = nullcontext
context.run_migrations = lambda: None
runpy.run_path(Path("alembic") / "env.py", run_name="alembic_env_under_test")
"""
    environment = {**os.environ, "DATABASE_URL": "sqlite:///application.db"}
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=backend_dir,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_alembic_environment_uses_explicit_validation_override() -> None:
    assert _read_alembic_environment_url(use_override=True) == "sqlite:///validator.db"


def test_alembic_environment_normally_uses_application_settings() -> None:
    assert _read_alembic_environment_url(use_override=False) == "sqlite:///application.db"


@pytest.mark.parametrize(
    ("tables", "views", "object_name"),
    ((["existing_table"], [], "existing_table"), ([], ["existing_view"], "existing_view")),
)
def test_database_with_existing_table_or_view_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tables: list[str],
    views: list[str],
    object_name: str,
) -> None:
    class Connection:
        def __enter__(self) -> Connection:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    class Engine:
        def connect(self) -> Connection:
            return Connection()

    class Inspector:
        def get_table_names(self) -> list[str]:
            return tables

        def get_view_names(self) -> list[str]:
            return views

    monkeypatch.setattr(validation, "inspect", lambda connection: Inspector())

    with pytest.raises(validation.ReleaseValidationError, match=object_name):
        validation.require_empty_database(Engine())  # type: ignore[arg-type]


@pytest.mark.parametrize("heads", ([], ["head_one", "head_two"]))
def test_alembic_requires_exactly_one_head(
    monkeypatch: pytest.MonkeyPatch, heads: list[str]
) -> None:
    class Scripts:
        def get_heads(self) -> list[str]:
            return heads

    monkeypatch.setattr(
        validation.ScriptDirectory, "from_config", lambda config: Scripts()
    )

    with pytest.raises(validation.ReleaseValidationError, match=re.escape(repr(heads))):
        validation.require_single_head(Config())


def test_schema_drift_reports_useful_difference_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Connection:
        def __enter__(self) -> Connection:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    class Engine:
        def connect(self) -> Connection:
            return Connection()

    difference = ("add_column", None, "users", "display_name")
    monkeypatch.setattr(validation, "schema_differences", lambda connection: [difference])

    with pytest.raises(validation.ReleaseValidationError) as error:
        validation.require_no_schema_drift(Engine())  # type: ignore[arg-type]

    assert "ORM-to-migration schema drift detected" in str(error.value)
    assert "add_column" in str(error.value)
    assert "display_name" in str(error.value)


def test_current_revision_must_match_expected_head(monkeypatch: pytest.MonkeyPatch) -> None:
    class Connection:
        def __enter__(self) -> Connection:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    class Engine:
        def connect(self) -> Connection:
            return Connection()

    class Context:
        def get_current_revision(self) -> str:
            return "old_revision"

    monkeypatch.setattr(
        validation.RuntimeMigrationContext,
        "configure",
        lambda connection: Context(),
    )

    with pytest.raises(
        validation.ReleaseValidationError,
        match="expected current_head, found old_revision",
    ):
        validation.require_current_head(Engine(), "current_head")  # type: ignore[arg-type]


def _prepare_orchestration(monkeypatch: pytest.MonkeyPatch) -> FakeEngine:
    engine = FakeEngine()
    monkeypatch.setattr(
        validation,
        "require_safe_validation_url",
        lambda value: make_url("postgresql://host/skdk_test"),
    )
    monkeypatch.setattr(validation, "build_alembic_config", lambda url: object())
    monkeypatch.setattr(validation, "require_single_head", lambda config: "expected_head")
    monkeypatch.setattr(validation, "create_engine", lambda url, **kwargs: engine)
    return engine


@pytest.mark.parametrize(
    "failing_step",
    ("upgrade_to_head", "validate_seed", "validate_metadata", "require_no_schema_drift"),
)
def test_validation_propagates_release_step_failures(
    monkeypatch: pytest.MonkeyPatch,
    failing_step: str,
) -> None:
    engine = _prepare_orchestration(monkeypatch)
    step_names = (
        "require_empty_database",
        "upgrade_to_head",
        "require_current_head",
        "validate_metadata",
        "validate_seed",
        "require_no_schema_drift",
    )
    for step_name in step_names:
        replacement: Callable[..., None] = lambda *args: None
        if step_name == failing_step:
            replacement = lambda *args: (_ for _ in ()).throw(
                RuntimeError("step exploded")
            )
        monkeypatch.setattr(validation, step_name, replacement)

    with pytest.raises(validation.ReleaseValidationError, match="step exploded"):
        validation.run_validation("explicit-value")

    assert engine.disposed is True


def test_engine_is_disposed_when_empty_database_check_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _prepare_orchestration(monkeypatch)
    monkeypatch.setattr(
        validation,
        "require_empty_database",
        lambda engine: (_ for _ in ()).throw(
            validation.ReleaseValidationError("existing table")
        ),
    )

    with pytest.raises(validation.ReleaseValidationError, match="existing table"):
        validation.run_validation("explicit-value")

    assert engine.disposed is True


def test_successful_validation_runs_every_step_in_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _prepare_orchestration(monkeypatch)
    events: list[str] = []
    for step_name in (
        "require_empty_database",
        "upgrade_to_head",
        "require_current_head",
        "validate_metadata",
        "validate_seed",
        "require_no_schema_drift",
    ):
        monkeypatch.setattr(
            validation,
            step_name,
            lambda *args, name=step_name: events.append(name),
        )

    validation.run_validation("explicit-value")

    assert events == [
        "require_empty_database",
        "upgrade_to_head",
        "require_current_head",
        "validate_metadata",
        "validate_seed",
        "require_no_schema_drift",
    ]
    assert engine.disposed is True


def test_main_returns_nonzero_with_clear_validation_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv(validation.VALIDATION_URL_ENV, raising=False)

    assert validation.main() == 1
    assert "must be explicitly set" in capsys.readouterr().err


def test_main_returns_nonzero_for_unexpected_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        validation,
        "run_validation",
        lambda value: (_ for _ in ()).throw(RuntimeError("connection failed")),
    )

    assert validation.main() == 1
    assert "failed unexpectedly: connection failed" in capsys.readouterr().err
