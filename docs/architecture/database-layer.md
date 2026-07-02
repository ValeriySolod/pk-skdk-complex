# Database Layer Architecture

## Current stack

The backend database layer is built for the existing Python/FastAPI application.
It uses SQLAlchemy 2.x for ORM mapping and session management, PostgreSQL as the
target production database, and Alembic as the planned migration tool. The local
default `DATABASE_URL` currently points to SQLite so the backend can run without
external infrastructure during development.

Prisma is not used in this backend because the service is Python/FastAPI, not
Node.js. SQLAlchemy and Alembic match the runtime, dependency set, and existing
model code already present in the repository.

## Responsibilities

The database layer owns backend concerns that are shared across modules:

- SQLAlchemy engine configuration.
- Database session factory configuration.
- FastAPI database session dependency.
- Declarative base class used by ORM models.
- Future repository infrastructure and transaction conventions.
- Migration and seed entry points.

It does not own HTTP routing, authentication rules, business workflow logic, or
Pydantic request and response schemas.

## Package layout

Canonical database exports live in `backend/app/database/`:

```txt
backend/app/database/
  __init__.py
  session.py
```

`backend/app/database/session.py` defines:

- `engine`
- `SessionLocal`
- `Base`
- `get_db`

`backend/app/database/__init__.py` re-exports those names for application code.
New code should import database primitives from `app.database`.

`backend/app/core/database.py` remains as a compatibility module and re-exports
the same objects. Existing imports from `app.core.database` continue to work
while modules are migrated gradually.

## Models

ORM models continue to live in `backend/app/models/`.

The model package is responsible for table definitions, relationships, enums,
and model exports. Models should remain framework-neutral and should not contain
FastAPI router code or request/response schema definitions.

## Engine and sessions

Engine and session configuration lives in `backend/app/database/session.py`.

The engine is created from `settings.DATABASE_URL`. SQLite receives the
`check_same_thread=False` connection argument for local development, while
PostgreSQL uses the default SQLAlchemy connection behavior. `SessionLocal` is
configured with `autoflush=False` and `autocommit=False`.

FastAPI routes should receive sessions through `Depends(get_db)`. Application
code should not create long-lived global sessions.

## Future repositories

Future CRUD repositories should be added after this architecture skeleton, one
module at a time. Repository code should:

- Accept a SQLAlchemy `Session` from the caller.
- Keep query logic out of routers.
- Return ORM models or well-defined domain results.
- Avoid committing unless the repository method explicitly owns a full
  transaction boundary.
- Live near the owning business module or in a dedicated repository package once
  a consistent convention is introduced.

This pass intentionally does not create CRUD repositories.

## Migrations and seed

Alembic should be used for database schema migrations. Migration scripts should
capture schema changes, remain reviewable, and be run as part of deployment or
release workflow once migration configuration is finalized.

`backend/app/seed.py` remains the seed entry point for development data. Seed
logic should be idempotent, use the same SQLAlchemy session configuration as the
application, and avoid replacing migration scripts.

`Base.metadata.create_all(bind=engine)` is still present in existing startup and
seed paths for current compatibility. It should be revisited when Alembic
migrations become the authoritative schema management workflow.
