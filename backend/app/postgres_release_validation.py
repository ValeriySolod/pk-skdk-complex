from __future__ import annotations

import os
import re
import sys
from collections.abc import Callable
from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.runtime.migration import MigrationContext as RuntimeMigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Connection, Engine, URL, make_url
from sqlalchemy.orm import configure_mappers, sessionmaker

from app.db.model_registration import register_models


VALIDATION_URL_ENV = "POSTGRES_VALIDATION_DATABASE_URL"
ALEMBIC_VALIDATION_URL_ATTRIBUTE = "postgres_release_validation_database_url"
DISPOSABLE_DATABASE_MARKERS = (
    "test",
    "testing",
    "validation",
    "validate",
    "disposable",
    "ci",
)


class ReleaseValidationError(RuntimeError):
    """A PostgreSQL release condition was not satisfied."""


def require_safe_validation_url(value: str | None) -> URL:
    if not value:
        raise ReleaseValidationError(f"{VALIDATION_URL_ENV} must be explicitly set")

    try:
        url = make_url(value)
    except Exception as error:
        raise ReleaseValidationError(
            f"{VALIDATION_URL_ENV} is not a valid database URL"
        ) from error

    if url.get_backend_name() != "postgresql":
        raise ReleaseValidationError(
            "validation requires a PostgreSQL URL; SQLite and other databases "
            "are refused"
        )

    database_name = (url.database or "").lower()
    markers = "|".join(DISPOSABLE_DATABASE_MARKERS)
    marker_pattern = rf"(?:^|[_-])(?:{markers})(?:$|[_-])"
    if not database_name or re.search(marker_pattern, database_name) is None:
        raise ReleaseValidationError(
            "PostgreSQL database name must clearly contain a disposable/test-only marker: "
            + ", ".join(DISPOSABLE_DATABASE_MARKERS)
        )
    return url


def build_alembic_config(database_url: URL) -> Config:
    backend_dir = Path(__file__).resolve().parents[1]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    config.attributes[ALEMBIC_VALIDATION_URL_ATTRIBUTE] = database_url
    return config


def require_single_head(config: Config) -> str:
    heads = ScriptDirectory.from_config(config).get_heads()
    if len(heads) != 1:
        raise ReleaseValidationError(f"expected exactly one Alembic head, found {heads}")
    return heads[0]


def require_empty_database(engine: Engine) -> None:
    with engine.connect() as connection:
        inspector = inspect(connection)
        objects = sorted({*inspector.get_table_names(), *inspector.get_view_names()})
    if objects:
        raise ReleaseValidationError(
            "validation database is not empty; refusing to alter it (existing tables/views: "
            + ", ".join(objects)
            + ")"
        )


def upgrade_to_head(config: Config) -> None:
    command.upgrade(config, "head")


def require_current_head(engine: Engine, expected_head: str) -> None:
    with engine.connect() as connection:
        actual_head = RuntimeMigrationContext.configure(connection).get_current_revision()
    if actual_head != expected_head:
        raise ReleaseValidationError(
            f"Alembic revision mismatch: expected {expected_head}, found {actual_head or '<none>'}"
        )


def validate_metadata(engine: Engine) -> None:
    metadata = register_models()
    configure_mappers()
    with engine.connect() as connection:
        actual_tables = set(inspect(connection).get_table_names())
    missing_tables = set(metadata.tables) - actual_tables
    if missing_tables:
        raise ReleaseValidationError(
            "migrated schema is missing ORM tables: "
            + ", ".join(sorted(missing_tables))
        )


def validate_seed(engine: Engine) -> None:
    from app.seed import SEED_OPERATIONS, seed_database

    seed_database(session_factory=sessionmaker(bind=engine))
    if SEED_OPERATIONS:
        print(f"[ok] seed workflow ({len(SEED_OPERATIONS)} registered operation(s))")
    else:
        print("[ok] seed workflow (no production seed operations registered)")


def schema_differences(connection: Connection) -> list[object]:
    context = MigrationContext.configure(
        connection,
        opts={"compare_type": True, "compare_server_default": True},
    )
    return list(compare_metadata(context, register_models()))


def require_no_schema_drift(engine: Engine) -> None:
    with engine.connect() as connection:
        differences = schema_differences(connection)
    if differences:
        details = "\n".join(f"  - {difference!r}" for difference in differences)
        raise ReleaseValidationError(f"ORM-to-migration schema drift detected:\n{details}")


ValidationStep = tuple[str, Callable[[], None]]


def run_validation(database_url_value: str | None) -> None:
    database_url = require_safe_validation_url(database_url_value)
    config = build_alembic_config(database_url)
    expected_head = require_single_head(config)
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        steps: tuple[ValidationStep, ...] = (
            (
                "empty PostgreSQL database confirmed",
                lambda: require_empty_database(engine),
            ),
            ("Alembic upgrade reached head", lambda: upgrade_to_head(config)),
            (
                "database revision matches Alembic head",
                lambda: require_current_head(engine, expected_head),
            ),
            (
                "canonical metadata and mappers validated",
                lambda: validate_metadata(engine),
            ),
            ("registered seed workflow completed", lambda: validate_seed(engine)),
            (
                "no ORM-to-migration schema drift",
                lambda: require_no_schema_drift(engine),
            ),
        )
        for label, step in steps:
            try:
                step()
            except ReleaseValidationError:
                raise
            except Exception as error:
                raise ReleaseValidationError(f"{label} failed: {error}") from error
            print(f"[ok] {label}")
    finally:
        engine.dispose()
    print(f"PostgreSQL release validation passed at Alembic head {expected_head}.")


def main() -> int:
    try:
        run_validation(os.environ.get(VALIDATION_URL_ENV))
    except ReleaseValidationError as error:
        print(f"PostgreSQL release validation failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(
            f"PostgreSQL release validation failed unexpectedly: {error}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
