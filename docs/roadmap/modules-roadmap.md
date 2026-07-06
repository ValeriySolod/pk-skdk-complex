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
| MOD-007 | Audit Log | ✅ | User activity log, change history, security audit; MOD-007.1 audit log architecture skeleton created; MOD-007.2 audit log domain model skeletons added; MOD-007.3 audit log Alembic migration added; MOD-007.4 audit log repository skeleton added; MOD-007.5 audit log service skeleton implemented; MOD-007.6 audit log schemas/API contract added; MOD-007.7 repository/database tests added; MOD-007.8 service tests/business logic checks added; MOD-007.9 API/business tests added; MOD-007.10 completed after readiness sweep |
| MOD-008 | File Storage | ✅ | File upload, download, metadata, access rules; MOD-008.1 architecture skeleton created; MOD-008.2 domain model skeletons created; MOD-008.3 database migration added; MOD-008.4 repository skeleton added; MOD-008.5 service skeleton added; MOD-008.6 schemas and API contract tests added; MOD-008.7 repository tests / database integration checks added; MOD-008.8 service tests / business logic checks added; MOD-008.9 API business tests added; MOD-008.10 completed after readiness sweep |
| MOD-009 | Notifications | ✅ | In-app notifications, email notifications, system alerts; MOD-009.1 architecture skeleton created; MOD-009.2 notifications domain model skeletons added; MOD-009.3 notifications database migration added; MOD-009.4 notifications repository skeleton added; MOD-009.5 notifications service skeleton added; MOD-009.6 notifications schemas and API contract tests added; MOD-009.7 notifications repository/database tests added; MOD-009.8 notifications service tests/business logic checks added; MOD-009.9 notifications API business tests added; MOD-009.10 completed after readiness sweep |
| MOD-010 | Reporting & Analytics | ✅ | Dashboards, statistics, printable/exportable reports; MOD-010.1 reporting and analytics architecture skeleton created; MOD-010.2 reporting and analytics domain models added; MOD-010.3 reporting analytics database migration added; MOD-010.4 reporting and analytics repository skeleton added; MOD-010.5 reporting and analytics service skeleton added; MOD-010.6 reporting analytics schemas and API contract tests added; MOD-010.7 reporting analytics repository/database tests added; MOD-010.8 reporting analytics service tests/business logic checks added; MOD-010.9 reporting analytics API business/integration tests added; MOD-010.10 completed after readiness sweep |
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
| MOD-007.3 | Audit Log database migration / Alembic integration | ✅ | Audit log models imported into Alembic metadata and migration added |
| MOD-007.4 | Audit Log repository skeleton | ✅ | Thin SQLAlchemy repository helpers for creating, retrieving, listing, filtering, and counting audit log events added |
| MOD-007.5 | Audit Log service skeleton | ✅ | Thin service boundary over audit log repository operations implemented |
| MOD-007.6 | Audit Log schemas/API contract | ✅ | Pydantic schemas, skeleton-compatible API response contracts, and API contract tests added |
| MOD-007.7 | Audit Log repository tests / database integration checks | ✅ | Repository/database integration tests for audit log create, lookup, filtering, counting, ordering, pagination, and missing results added |
| MOD-007.8 | Audit Log service tests / business logic checks | ✅ | Service-layer tests for audit log create, lookup, UUID lookup, filtering, counting, ordering, pagination, JSON state, health, and missing event behavior added |
| MOD-007.9 | Audit Log API business tests / endpoint behavior checks | ✅ | FastAPI TestClient endpoint behavior tests added for audit log create, list, detail, UUID lookup, filters, pagination, date range, JSON state, validation, and missing event responses |
| MOD-007.10 | Audit Log module completion / readiness sweep | ✅ | Completion follows readiness sweep after repository, service, contract, and API/business test coverage |
| MOD-008.1 | File Storage architecture skeleton | ✅ | File storage module package, routes, service, repository, and schemas skeleton added |
| MOD-008.2 | File Storage domain model skeletons | ✅ | SQLAlchemy domain model skeleton for file storage metadata and lifecycle state added |
| MOD-008.3 | File Storage database migration | ✅ | Alembic migration added for file storage metadata table |
| MOD-008.4 | File Storage repository skeleton | ✅ | File Storage repository skeleton added |
| MOD-008.5 | File Storage service skeleton | ✅ | File Storage service orchestration layer added for metadata lifecycle operations over the repository |
| MOD-008.6 | File Storage schemas / API contract tests | ✅ | Pydantic schemas completed for file objects; skeleton-compatible API routes and contract tests added |
| MOD-008.7 | File Storage repository tests / database integration checks | ✅ | Repository/database integration checks added for file object persistence, lookup, filtering, pagination, updates, soft delete lifecycle, health, and missing records |
| MOD-008.8 | File Storage service tests / business logic checks | ✅ | Service-layer tests added for file object registration, lookup aliases, filtering, pagination, counting, updates, soft delete lifecycle, UUID stability, metadata, health, and missing records |
| MOD-008.9 | File Storage API business tests / endpoint behavior checks | ✅ | FastAPI TestClient endpoint behavior tests added for file object create, list, detail, UUID lookup, filters, pagination, metadata preservation, validation, and missing object responses |
| MOD-008.10 | File Storage module completion / readiness sweep | ✅ | Final readiness sweep completed: models, repository, service, schemas, routes, Alembic integration, migration, module registration, lifecycle behavior, lookup consistency, pagination, validation, health, and tests reviewed; no backend changes required |
| MOD-009.1 | Notifications architecture skeleton | ✅ | Notifications module package, registry wiring, routes, service, repository, and schemas skeleton added |
| MOD-009.2 | Notifications domain models | ✅ | SQLAlchemy domain models and enum-like lifecycle constants added for notifications and delivery tracking |
| MOD-009.3 | Notifications database migration | ✅ | Alembic migration added for notifications and delivery tracking tables |
| MOD-009.4 | Notifications repository skeleton | ✅ | SQLAlchemy repository skeletons added for notifications and delivery tracking |
| MOD-009.5 | Notifications service skeleton | ✅ | Thin service-layer business boundary added for notifications and delivery tracking |
| MOD-009.6 | Notifications schemas / API contract tests | ✅ | Pydantic schemas completed for notifications and delivery tracking; skeleton-compatible API routes and contract tests added |
| MOD-009.7 | Notifications repository tests / database integration checks | ✅ | Repository/database integration tests added for notification persistence, lookup, filtering, pagination, updates, soft delete lifecycle, delivery tracking, status updates, aggregate repository health, UUID stability, and delivery access after notification soft delete |
| MOD-009.8 | Notifications service tests / business logic checks | ✅ | Service-layer tests added for notification and delivery create, lookup aliases, filtering, counting, updates, status changes, soft delete behavior, aggregate repository behavior, missing records, UUID stability, and lifecycle consistency |
| MOD-009.9 | Notifications API business tests / endpoint behavior checks | ✅ | FastAPI TestClient business tests added for notification and delivery create/read/list/count behavior, UUID lookup consistency, filtering, pagination, validation errors, missing records, and soft-delete visibility where routes support it |
| MOD-009.10 | Notifications module completion / readiness sweep | ✅ | Final readiness sweep completed: models, repository, service, schemas, routes, Alembic integration, migration, module registration, health, lifecycle behavior, lookup consistency, pagination, validation, and tests reviewed |
| MOD-010.1 | Reporting & Analytics architecture skeleton | ✅ | Reporting and analytics module package, routes, service, repository, and schemas skeleton added |
| MOD-010.2 | Reporting & Analytics domain models | ✅ | SQLAlchemy domain models and enum-like lifecycle constants added for dashboards, report definitions, report runs, and analytics snapshots |
| MOD-010.3 | Reporting & Analytics database migration | ✅ | Alembic migration added for dashboards, report definitions, report runs, and analytics snapshots |
| MOD-010.4 | Reporting & Analytics repository skeleton | ✅ | SQLAlchemy repository helpers added for dashboards, report definitions, report runs, and analytics snapshots |
| MOD-010.5 | Reporting & Analytics service skeleton | ✅ | Thin service-layer business boundary added for dashboards, report definitions, report runs, and analytics snapshots |
| MOD-010.6 | Reporting & Analytics schemas and API contract tests | ✅ | Pydantic API schemas and basic FastAPI contract tests added for reporting and analytics health/schema surface |
| MOD-010.7 | Reporting & Analytics repository tests / database integration checks | ✅ | Repository/database integration tests added for dashboards, report definitions, report runs, analytics snapshots, filtering, pagination, updates, lifecycle behavior, health, UUID stability, and missing records |
| MOD-010.8 | Reporting & Analytics service tests / business logic checks | ✅ | Service-layer business logic tests added for dashboard lifecycle, report definition aliases/filtering/soft delete, report run lifecycle/relationships, analytics snapshot aliases/filtering/update behavior, health, UUID stability, counts, and missing records |
| MOD-010.9 | Reporting & Analytics API business tests / route integration checks | ✅ | API business/integration tests added for reporting analytics health, dashboard/report/run/snapshot persistence, response shape, filtering/counts, UUID/id lookups, and missing/invalid input handling |
| MOD-010.10 | Reporting & Analytics completion / readiness sweep | ✅ | Final readiness sweep completed: models, repository, service, schemas, routes, module registration, aggregate health, lifecycle behavior, API compatibility, and tests reviewed |
