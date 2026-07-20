# DEV-010 Real Browser Frontend-Backend Integration Validation

Verdict: **PASS**
Validation date: 2026-07-20

## Scope

This increment validates the DEV-006 through DEV-009 read-only frontend-backend
flows. It does not change frontend or backend behavior. All evidence below is
sanitized: credentials, bearer tokens, authorization header values, JWT signing
material, and database connection URLs are intentionally omitted.

## Environment

- Browser: Codex in-app browser, real browser session
- Frontend: React/Vite development server at `http://127.0.0.1:5173`
- Backend: FastAPI/Uvicorn at `http://127.0.0.1:8000`
- API root: `http://127.0.0.1:8000/api/v1`
- Demo mode: disabled (`VITE_DEMO_MODE` unset)
- Database: dedicated local PostgreSQL 17 validation database
  `pk_skdk_dev010_validation`
- Migration state: all 13 Alembic revisions applied; current head
  `20260709_0013`
- Schema validation: canonical metadata and mapper checks passed; no
  ORM-to-migration drift
- Authentication: one active local test administrator created in the dedicated
  validation database using the repository-documented development login; no
  secret value is recorded here
- Mocks: none; both servers and PostgreSQL were running during the completed
  browser checks

The existing configured development database was not used because it contained
application tables without an Alembic revision. An attempted migration failed
closed on the first duplicate table. It was not stamped, reset, truncated, or
otherwise modified. The dedicated validation database was created instead.

## Commands

The following commands are sanitized. Database URLs and credentials were
derived locally without being printed.

```text
backend\.venv\Scripts\python.exe -m app.postgres_release_validation
backend\.venv\Scripts\python.exe <sanitized test-user creation check>
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
npm.cmd run dev -- --host 127.0.0.1 --port 5173
npm.cmd test
npm.cmd run build
backend\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp <writable-scratch>
backend\.venv\Scripts\python.exe -m compileall -q app tests alembic
git diff --check
```

## Browser results

| Check | Expected | Actual | Result |
|---|---|---|---|
| Login | Real `POST /api/v1/auth/login` authenticates the test user | Login completed and the protected application shell rendered | PASS |
| Current user | Real `GET /api/v1/auth/me` returns and renders the authenticated user | Sanitized full name, username, and backend role rendered in the shell | PASS |
| Open `/organizations` | Protected route renders after authentication | Route opened in the authenticated session | PASS |
| Organization units | Real `GET /api/v1/organization-structure/units` drives an independent state | Legitimate `No organization units found` empty state rendered | PASS |
| Positions | Real `GET /api/v1/organization-structure/positions` drives an independent state | Legitimate `No positions found` empty state rendered | PASS |
| Employee assignments | Real `GET /api/v1/organization-structure/assignments` drives an independent state | Legitimate `No employee assignments found` empty state rendered | PASS |
| Refresh | Session is restored through the stored bearer token and `/auth/me` | Refresh remained on `/organizations`; user and all three empty states rendered again | PASS |
| Logout | Token is cleared and navigation returns to `/login` | Logout returned to `/login`; protected shell was absent | PASS |
| Invalid/expired token | Active 401 clears the session, redirects to `/login`, and stale requests cause no side effects | A synthetic invalid token caused `GET /api/v1/auth/me` to return HTTP 401; no protected organization data loaded afterward, authenticated state was cleared, and the browser redirected to `/login` without an HTTP 500 response | PASS |
| Network inspection | Record browser request URLs, response codes, authorization and CORS behavior without secrets | Real login, current-user, organization-unit, position, and assignment flows completed against the configured API root with bearer authentication; the invalid-token request returned the expected 401, CORS permitted the Vite origin, and no console error or HTTP 500 was observed | PASS |
| Demo/legacy Axios exclusion | Validated flows use neither demo loaders nor the deprecated Axios client | Demo mode was disabled. Source and focused-test review confirm `/auth/me` and all three organization reads use the canonical Fetch client; the deprecated Axios client is limited to unrelated legacy modules | PASS |

## Sanitized observations

- The application shell rendered the dedicated test user's sanitized full name,
  username, and backend-provided administrator role.
- `/organizations` rendered three independent legitimate empty states from the
  empty migrated validation database.
- Refresh restored the authenticated route and repeated all three independent
  results.
- Logout returned to `/login`.
- Manual invalid-token validation confirmed an HTTP 401 from `/auth/me`, no
  subsequent protected organization-data load, authenticated-state clearing,
  and redirection to `/login`.
- Re-login with the existing DEV-010 test administrator succeeded.
- Browser console inspection returned no warning or error entries, and no HTTP
  500 response was observed.
- Frontend and backend health probes returned HTTP 200 before browser testing.
- No token, cookie, authorization header value, password, signing secret, or
  database URL was copied into this evidence.

## Final verdict

All required DEV-010 browser flows passed against the real non-demo FastAPI,
Vite, and migrated PostgreSQL environment. The manual invalid-token check
completed the active-401 validation without exposing the token value. No
frontend or backend integration defect was found.

## Automated verification

- Complete frontend suite: **59 passed**.
- Frontend production build (`tsc -b && vite build`): **passed**.
- Complete backend suite: **413 passed** in 81.97 seconds.
- Backend compilation (`app`, `tests`, and `alembic`): **passed**.
- These checks support the implementation contracts and were complemented by
  the completed real-browser validation above.
