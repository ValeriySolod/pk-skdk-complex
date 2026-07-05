# PK SKDK Modules Roadmap

## Purpose

This document is the source of truth for application module tasks in the PK SKDK project.

Each module task has a unique identifier (`MOD-XXX`) that never changes after being assigned.

---

# Modules

| ID | Module | Status | Notes |
|----|--------|--------|-------|
| MOD-001 | Modules roadmap | ✅ | Initial modules roadmap created |
| MOD-002 | Authentication & Authorization | ✅ | Planned; MOD-002.1 authentication architecture skeleton created; MOD-002.2 authenticated application shell wired to module routes; MOD-002.3 dynamic module registry implemented; MOD-002.4 protected routes added; MOD-002.5 role-based route authorization completed; MOD-002.6 access denied page completed |
| MOD-003 | Database Layer | ⬜ | SQLAlchemy, PostgreSQL, migrations, seed, database initialization; MOD-003.1 database architecture skeleton created; MOD-003.2 SQLAlchemy base foundation completed; MOD-003.3 preserved; MOD-003.4 database base infrastructure completed; MOD-003.6 database compatibility cleanup completed; MOD-003.7 Alembic migration environment and initial schema migration added; MOD-003.9 repository layer added; MOD-003.10 database service layer skeleton added; MOD-003.11 database seed foundation added; MOD-003.12 database healthcheck endpoint added; MOD-003.14 health service refactor completed; MOD-003.16 database healthcheck tests added; MOD-003.17 database seed tests added; MOD-003.18 legacy database compatibility package removed |
| MOD-004 | Organization Structure | ✅ | Organizational hierarchy, departments, positions, employees; MOD-004.1 organization structure architecture skeleton created; MOD-004.2 organization structure domain model skeleton added; MOD-004.4 organization structure repository skeleton added; MOD-004.5 organization structure service skeleton added; MOD-004.6 organization structure API routes skeleton added; MOD-004.7 organization structure API integration smoke tests added; MOD-004.8 organization structure Alembic migration added; MOD-004.9 organization structure repository database integration tests added; MOD-004.10 organization structure service tests added; MOD-004.11 organization structure API business tests added; MOD-004.12 organization structure module completion review / stabilization completed |
| MOD-005 | User Management | ✅ | User CRUD, role assignment, permissions management; MOD-005.1 user management architecture skeleton created; MOD-005.2 user management domain model skeletons added; MOD-005.3 user management schema skeletons added; MOD-005.4 user management repository skeleton added; MOD-005.5 user management service skeleton added; MOD-005.6 user management API routes skeleton added; MOD-005.7 user management API smoke tests added; MOD-005.8 user management Alembic migration added; MOD-005.9 user management repository database integration tests added; MOD-005.10 user management service tests added; MOD-005.11 user management API business tests added; MOD-005.12 user management stabilization completed |
| MOD-006 | Document Management | ✅ | Document storage, metadata, versioning, attachments; MOD-006.1 architecture skeleton created; MOD-006.2 document management domain model skeletons added; MOD-006.3 document management repository skeleton added; MOD-006.4 document management service skeleton added; MOD-006.5 document management API routes skeleton added; MOD-006.6 schemas and API contract tests added; MOD-006.7 document management Alembic migration added; MOD-006.8 repository integration tests added; MOD-006.9 service tests added; MOD-006.10 API business tests added; MOD-006.11 completed after readiness sweep |
| MOD-007 | Audit Log | ⬜ | User activity log, change history, security audit; MOD-007.1 audit log architecture skeleton created; MOD-007.2 audit log domain model skeletons added |
| MOD-008 | File Storage | ⬜ | File upload, download, metadata, access rules |
| MOD-009 | Notifications | ⬜ | In-app notifications, email notifications, system alerts |
| MOD-010 | Reporting & Analytics | ⬜ | Dashboards, statistics, printable/exportable reports |
| MOD-011 | Administration | ⬜ | Application administration, reference data, maintenance tools |
| MOD-012 | System Settings | ⬜ | Configurable application settings and defaults |
| MOD-013 | Integrations | ⬜ | Email/API integrations and external service connections |
| MOD-014 | Backup & Restore | ⬜ | Backup creation, restore workflow, data recovery procedures |
| MOD-015 | Monitoring & Health | ⬜ | Health checks, diagnostics, operational monitoring |

---

# Development Tasks

| ID | Task | Status | Notes |
|----|------|--------|-------|
| DEV-001 | Git Bash Workflow Scripts | ✅ | Git Bash helper scripts and documentation created |
| MOD-004.3 | Organization Structure schemas skeleton | ✅ | Pydantic schema skeletons added |
| MOD-004.4 | Organization Structure repository skeleton | ✅ | SQLAlchemy repository skeletons added |
| MOD-004.5 | Organization Structure service skeleton | ✅ | Thin service layer skeleton added |
| MOD-004.6 | Organization Structure API routes skeleton | ✅ | FastAPI route skeleton added |
| MOD-004.7 | Organization Structure API integration checks / smoke tests | ✅ | FastAPI route registration and basic request/response smoke tests added |
| MOD-004.8 | Organization Structure database migration / Alembic integration | ✅ | Organization structure models imported into Alembic metadata and migration added |
| MOD-004.9 | Organization Structure repository database integration tests | ✅ | SQLAlchemy repository integration tests added |
| MOD-004.10 | Organization Structure service tests / business logic checks | ✅ | Service-layer business logic tests added |
| MOD-004.11 | Organization Structure API business tests / endpoint behavior checks | ✅ | Business-level API endpoint behavior tests added |
| MOD-004.12 | Organization Structure module completion review / stabilization | ✅ | Final consistency, correctness, typing, import, test reliability, and roadmap status review completed |
| MOD-005.1 | User Management architecture skeleton | ✅ | User management module package, manifest, routes, service, repository, and schemas skeleton added |
| MOD-005.2 | User Management domain model skeletons | ✅ | SQLAlchemy domain models for user profiles, role assignments, and audit events added |
| MOD-005.3 | User Management schemas skeleton | ✅ | Pydantic schema skeletons for profiles, role assignments, and audit events added |
| MOD-005.4 | User Management repository skeleton | ✅ | SQLAlchemy repository skeletons for profiles, role assignments, audit events, and user lookups added |
| MOD-005.5 | User Management service skeleton | ✅ | Service-layer business boundary for profiles, role assignments, audit events, and user lookups added |
| MOD-005.6 | User Management API routes skeleton | ✅ | FastAPI route skeletons for users, profiles, role assignments, and audit events added |
| MOD-005.7 | User Management API smoke tests / endpoint registration checks | ✅ | User management API route registration and health endpoint smoke tests added |
| MOD-005.8 | User Management database migration / Alembic integration | ✅ | User management models imported into Alembic metadata and migration added |
| MOD-005.9 | User Management repository tests / database integration checks | ✅ | Repository-level database integration tests added for profiles, role assignments, audit events, transaction rollback, uniqueness, and foreign-key behavior |
| MOD-005.10 | User Management service tests / business logic checks | ✅ | Service-layer business logic tests for profiles, role assignments, audit events, and user lookups added |
| MOD-005.11 | User Management API business tests / endpoint behavior checks | ✅ | Business-level API endpoint behavior tests added for profiles, role assignments, audit events, and user lookups |
| MOD-005.12 | User Management module completion review / stabilization | ✅ | Final stabilization completed: imports, typing, route/service/repository boundaries, tests, and roadmap status reviewed |
| MOD-006.1 | Document Management architecture skeleton | ✅ | Document management module architecture skeleton created |
| MOD-006.2 | Document Management domain model skeletons | ✅ | SQLAlchemy domain models for documents, versions, categories, tags, permissions, and audit events added |
| MOD-006.3 | Document Management repository skeleton | ✅ | SQLAlchemy repository skeletons for documents, versions, categories, and attachments added |
| MOD-006.4 | Document Management service skeleton | ✅ | Service-layer business boundary for documents, versions, categories, and attachments added |
| MOD-006.5 | Document Management API routes skeleton | ✅ | FastAPI route skeletons for documents, versions, categories, attachments, and status helpers added |
| MOD-006.6 | Document Management schemas / API contract tests | ✅ | Pydantic schemas completed for documents, versions, categories, and attachments; API response contract tests added |
| MOD-006.7 | Document Management database migration / Alembic integration | ✅ | Document management models imported into Alembic metadata and migration added |
| MOD-006.8 | Document Management repository tests / database integration checks | ✅ | Repository/database integration tests for documents, versions, categories, and attachments added |
| MOD-006.9 | Document Management service tests / business logic checks | ✅ | Service-layer business logic tests for documents, versions, categories, attachments, status helpers, UUID lookup, and missing entity guards added |
| MOD-006.10 | Document Management API business tests / endpoint behavior checks | ✅ | Business-level API endpoint behavior tests added for documents, versions, categories, attachments, and status/lookup behavior |
| MOD-006.11 | Document Management completion / readiness sweep | ✅ | Final readiness sweep completed: models, repositories, services, schemas, routes, Alembic integration, migrations, and tests reviewed; no backend changes required |
| MOD-007.1 | Audit Log architecture skeleton | ✅ | Audit log module package, registry manifest, routes, service, repository, and schemas skeleton added |
| MOD-007.2 | Audit Log domain model skeletons | ✅ | SQLAlchemy domain model skeleton for audit log events added |
