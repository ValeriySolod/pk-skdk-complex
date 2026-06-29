# AGENTS.md

## Project

ПК СКДК complex.

Stack:
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: React + TypeScript + Vite
- Styling: CSS Modules
- Routing: React Router

Architecture:
- `frontend/src/shared/ui` — reusable universal UI kit
- `frontend/src/modules` — business modules
- `frontend/src/app` — app routes and shell
- `frontend/src/api` — API client layer
- `backend` — FastAPI backend
- `docs` — project documentation

## General rules

- Production-quality code only.
- TypeScript without `any`.
- Keep components reusable and isolated.
- Use CSS Modules for component styles.
- Preserve existing architecture and naming conventions.
- Do not introduce new dependencies unless explicitly requested.
- Prefer small, focused changes.
- Do not rewrite unrelated files.
- Do not change backend code unless the task explicitly requires it.
- Do not change public APIs of existing components unless explicitly requested.
- Keep accessibility in mind for every UI component.

## Shared UI component rules

Every shared UI component must:

- Live in its own folder inside `frontend/src/shared/ui`.
- Have this structure:

```txt
ComponentName/
  ComponentName.tsx
  ComponentName.module.css
  index.ts