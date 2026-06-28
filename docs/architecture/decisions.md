# Architecture Decisions

## ADR-001 — Use `shared/ui` as the only UI Kit location

Status: Accepted  
Date: 2026-06-28

Reusable UI components must be created only in:

`frontend/src/shared/ui`

`frontend/src/shared/components` must not be expanded.

Reason:

- Avoid duplicated UI components.
- Keep imports predictable.
- Make future refactoring safer.

## ADR-002 — One task, one logical change

Status: Accepted  
Date: 2026-06-28

Each task must contain one completed change only.

Reason:

- Easier review.
- Easier rollback.
- Lower risk of broken builds.