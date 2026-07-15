# Backend Integration and Readiness

## Verified integration boundaries

The FastAPI application loads module manifests through `app.modules_loader` and
registers each manifest router below `/api/v1/<module-code>`. Public application
and database health endpoints remain separate from protected business-module
routes. Protected routes use the shared `get_current_user` dependency, and
database-backed routes obtain request-scoped sessions through `get_db`.

`app.db.model_registration.register_models()` is the canonical ORM registration
entry point. It imports the production model set into the shared `Base.metadata`;
Alembic uses the same entry point for autogeneration and migration comparison.

## Database lifecycle

Alembic is the only production schema-management path. Application import and
startup do not call `metadata.create_all`. Deployments and fresh environments
must run the following from `backend` before the service starts:

```text
alembic heads
alembic upgrade head
python -m app.seed
uvicorn app.main:app
```

The seed step is optional while no production seed operations are registered.
It expects an existing, migrated schema and owns commit, rollback, and session
closure for the registered operations.

Request database sessions are closed unconditionally. Exceptions escaping a
request dependency cause a rollback before closure. Routes that translate
database integrity failures into client responses roll back before reusing the
session.

## Release verification

The project-wide readiness regression suite checks:

- the exact registered module set and route prefixes;
- uniqueness of route path/method combinations;
- canonical metadata size and SQLAlchemy mapper/relationship configuration;
- authenticated and unauthenticated behavior on a representative protected
  module health endpoint;
- absence of schema mutation during application startup;
- a clean SQLite test-database upgrade through the single Alembic head.

SQLite supplies deterministic migration and integration coverage but does not
replace PostgreSQL verification. Before a production release, run the full
backend test suite and an empty-database upgrade against the supported
PostgreSQL version, then inspect any autogeneration diff without applying an
unreviewed migration.

## PostgreSQL release validation (DEV-003)

PostgreSQL validation is opt-in and uses only the dedicated
`POSTGRES_VALIDATION_DATABASE_URL` environment variable. It never falls back to
the application's `DATABASE_URL`. The target must use the PostgreSQL dialect,
and its database name must contain one of these case-insensitive underscore- or
hyphen-delimited markers:
`test`, `testing`, `validation`, `validate`, `disposable`, or `ci`. Use a
dedicated, empty database such as `skdk_release_validation`. The validator does
not create, drop, truncate, reset, or otherwise clean a database; it refuses a
target containing any existing table or view.

The validated URL is passed to Alembic through a dedicated programmatic
configuration attribute used only by this validator. Ordinary Alembic commands
continue to read `settings.DATABASE_URL`; a generic `sqlalchemy.url` value in
`alembic.ini` is not an application-configuration override.

From Git Bash on Windows, with the project virtual environment activated, run:

```bash
cd backend
export POSTGRES_VALIDATION_DATABASE_URL='postgresql+psycopg://USER:PASSWORD@HOST:5432/skdk_release_validation'
python -m app.postgres_release_validation
```

PowerShell may set the same opt-in variable with:

```powershell
cd backend
$env:POSTGRES_VALIDATION_DATABASE_URL = 'postgresql+psycopg://USER:PASSWORD@HOST:5432/skdk_release_validation'
python -m app.postgres_release_validation
```

The workflow verifies a single Alembic head, confirms the target is empty,
upgrades the full migration chain to `head`, checks the stored revision, calls
the canonical `register_models()` entry point and configures all mappers, runs
the registered seed workflow, and compares the live schema with ORM metadata
using Alembic's supported autogeneration comparison API. Drift is reported but
no migration is generated or applied. Every failed condition exits non-zero.

A successful run ends with output equivalent to:

```text
[ok] empty PostgreSQL database confirmed
[ok] Alembic upgrade reached head
[ok] database revision matches Alembic head
[ok] canonical metadata and mappers validated
[ok] seed workflow (no production seed operations registered)
[ok] registered seed workflow completed
[ok] no ORM-to-migration schema drift
PostgreSQL release validation passed at Alembic head 20260709_0013.
```

Troubleshooting:

- Missing-variable, wrong-dialect, and unsafe-name errors occur before a
  connection is opened. Set the dedicated variable explicitly; do not reuse a
  development or production database.
- An `existing tables` error means the target is not empty. Point the command
  at a different dedicated empty validation database. The validator will not
  clean the current target.
- Connection or authentication failures should be resolved in PostgreSQL host,
  port, credentials, access rules, and SSL settings in the explicit URL.
- A revision mismatch, migration exception, seed exception, mapper/metadata
  error, or reported autogeneration difference is a failed release condition.
  Review the migration or ORM change; never apply an autogenerated revision
  without review.
- The ordinary test suite remains SQLite-based and does not require PostgreSQL.
  A real successful run of this command is still required as release evidence.
