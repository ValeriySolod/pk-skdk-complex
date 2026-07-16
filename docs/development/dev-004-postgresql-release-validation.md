# DEV-004 PostgreSQL Release Validation Evidence

Result: **PASS**  
Validation date: 2026-07-16

## Environment

- Database: dedicated local disposable database `skdk_release_validation`
- Dialect and server: PostgreSQL 17.10
- Driver: psycopg 3.3.4
- Python: 3.13.12
- SQLAlchemy: 2.0.36
- Alembic: 1.14.0
- Credentials and connection URLs are intentionally omitted.

The database did not exist before validation. It was created specifically for
this run on the repository's configured local PostgreSQL server. No existing
development database was reset, truncated, migrated, or otherwise modified.
After validation, `skdk_release_validation` was dropped and its absence was
confirmed; no development, staging, production, or other valuable database was
removed.

## Sanitized workflow

Commands were run from `backend` with the project virtual environment. The
dedicated URL was supplied only through `POSTGRES_VALIDATION_DATABASE_URL`.

```text
python -m app.postgres_release_validation
python <sanitized live-database seed/idempotency and relationship check>
python -m pytest -q -p no:cacheprovider --basetemp <external-scratch> tests/test_postgres_release_validation.py tests/test_seed.py tests/test_project_readiness.py
python -m pytest -q -p no:cacheprovider --basetemp <external-scratch>
python -m compileall -q app tests alembic
git diff --check
```

## Results

- Connection: real PostgreSQL connection established; server reported 17.10.
- Alembic graph: exactly one head, `20260709_0013`.
- Migration start: empty database with no current revision.
- Migration finish: all 13 revisions upgraded in order; live revision exactly
  `20260709_0013`.
- Schema: 42 registered application tables; mapper configuration succeeded;
  PostgreSQL type/default comparison reported no ORM-to-migration drift.
- Relationships: 54 live foreign keys inspected; every referenced table belongs
  to the registered application schema.
- Seed: zero production seed operations are currently registered. The canonical
  seed process succeeded during validation and on two additional consecutive
  runs. All application-table row-count snapshots were identical, confirming
  idempotency of the current empty baseline.
- Focused validator, seed, and readiness tests: 37 passed.
- Full backend test suite: 405 passed.
- Python compilation (`app`, `tests`, and `alembic`): passed.
- Downgrade/upgrade was not run because the DEV-003 workflow does not define or
  support that lifecycle.

No repository defect was exposed by the real PostgreSQL validation. The first
focused pytest invocation encountered only a host temp-directory permission
error; redirecting pytest temporary files to external writable scratch storage
resolved it without a code change.
