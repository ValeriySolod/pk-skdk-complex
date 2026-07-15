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
