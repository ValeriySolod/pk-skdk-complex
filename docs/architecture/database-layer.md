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

Canonical database exports live in `backend/app/db/`:

```txt
backend/app/db/
  __init__.py
  base.py
  dependencies.py
  mixins.py
  session.py
```

`backend/app/db/base.py` defines:

- `Base`
- shared metadata with stable constraint naming conventions

`backend/app/db/session.py` defines:

- `engine`
- `SessionLocal`

`backend/app/db/dependencies.py` defines `get_db`, including rollback on request
failure and unconditional session closure. `backend/app/db/__init__.py` re-exports
the public database primitives for application code. Application code should
import database primitives from `app.db`.

Legacy `app.database` and `app.core.database` compatibility modules have been
removed so there is one database abstraction.

## Models

ORM models continue to live in `backend/app/models/`.

The model package is responsible for table definitions, relationships, enums,
and model exports. Models should remain framework-neutral and should not contain
FastAPI router code or request/response schema definitions.

## Engine and sessions

The SQLAlchemy declarative base and shared metadata live in
`backend/app/db/base.py`. The metadata defines stable names for indexes,
unique constraints, check constraints, foreign keys, and primary keys so future
Alembic migrations produce predictable operations.

Engine and session configuration lives in `backend/app/db/session.py`.

The engine is created from `settings.DATABASE_URL`. SQLite receives the
`check_same_thread=False` connection argument for local development. Genuinely
in-memory SQLite URLs also use a single shared connection so their schema and
data remain visible across application threads; file-backed SQLite databases do
not use that pool configuration. PostgreSQL uses the default SQLAlchemy
connection behavior. `SessionLocal` is configured with `autoflush=False` and
`autocommit=False`.

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

`Base.metadata.create_all(bind=engine)` currently runs when `backend/app/main.py`
is imported during application startup. The seed entry point does not create or
upgrade schema: `seed_database` runs registered operations against an existing
schema and manages their transaction. Alembic remains the production
schema-management mechanism; startup `create_all` is development compatibility
behavior rather than a replacement for migrations.
