# PK SKDK Repository Instructions

## Source of truth

- Treat the roadmaps and project documentation in `docs/` as authoritative for scope, architecture, contracts, and completion status.
- Inspect the relevant roadmap, architecture documents, configuration, tests, and current git status before editing.
- Keep this file project-wide and stable; do not copy task progress, completed-task lists, test counts, or detailed roadmap and architecture content into it.

## Scope and architecture

- Deliver one focused, fully completed, independently verifiable increment per task.
- Make the smallest complete change that satisfies the acceptance criteria; do not add unrelated refactoring, cleanup, renaming, formatting, features, or dependency upgrades.
- Preserve established user changes and avoid modifying unrelated files.
- Preserve the existing backend architecture: FastAPI, SQLAlchemy, Alembic, and PostgreSQL, including established router, service, repository, schema, model, transaction, and migration boundaries.
- Preserve the existing frontend architecture: React, TypeScript, Vite, React Router, and CSS Modules, including established `app`, `pages`, `modules`, `shared`, and API-client boundaries.
- Reuse canonical contracts and abstractions. Do not create parallel implementations, weaken security or validation, or change public behavior without explicit scope.
- Keep code, identifiers, branch names, commit messages, prompts, UI text, and technical documentation in English unless project requirements specify otherwise.

## Implementation and validation

- Add a regression test for every bug fix and relevant success, failure, boundary, and compatibility tests for new behavior.
- Validate in increasing scope: focused tests, all applicable backend and/or frontend tests, then configured compile, typecheck, lint, and build checks relevant to the change.
- Use repository configuration and documented scripts as the canonical commands; do not claim a check passed unless it was executed and its result observed.
- Before handoff, inspect the complete diff for correctness, security, data safety, stale contracts, missing callers, weak tests, and unrelated changes.
- Run `git diff --check` and inspect the final `git status`.
- Update authoritative documentation and roadmap entries only when the task changes behavior, architecture, contracts, setup, migrations, or completion status.

## Git safety

- Preserve all existing tracked and untracked user work.
- Do not commit, push, merge, rebase, delete branches, open pull requests, or create releases unless the user explicitly requests that action.
- Do not stage files, amend history, force-push, reset, or delete data unless explicitly authorized for an exact verified scope.

## Completion and handoff

- A task is complete only when its acceptance criteria are met, architecture and contracts are preserved, relevant tests and checks pass, the diff contains no unrelated changes, and required documentation is synchronized.
- Report what changed, the files or components affected, executed validations and results, remaining limitations or risks, and any action required from the user.
