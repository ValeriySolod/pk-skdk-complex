# PK SKDK Development Workflow

Version: 1.0

---

# 1. Purpose

This document defines the standard development workflow for the PK SKDK project.

It is the single source of truth for the development process and must be followed for every backend, frontend, UI Kit, infrastructure, documentation, and testing increment.

Project roadmaps define **what** should be implemented.

This document defines **how** it must be implemented.

---

# 2. Source of Truth

Always use the following documents:

| Document                        | Purpose                 |
| ------------------------------- | ----------------------- |
| docs/roadmap/modules-roadmap.md | Backend modules roadmap |
| docs/roadmap/ui-kit-roadmap.md  | UI Kit roadmap          |
| docs/development/workflow.md    | Development workflow    |

Roadmaps describe work items.

Workflow describes the implementation process.

---

# 3. General Principles

* Keep the repository production-ready.
* Complete one increment at a time.
* Never combine unrelated work.
* Follow existing project architecture.
* Prefer consistency over creativity.
* Keep commits focused.
* Keep Pull Requests small.
* Update documentation together with code.

---

# 4. Project Stack

Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL

Frontend

* React
* TypeScript
* Vite
* Next.js (where applicable)

Do not introduce new frameworks or architectural patterns unless explicitly approved.

---

# 5. Development Lifecycle

Every increment follows the same lifecycle:

1. Synchronize main
2. Review roadmap
3. Create feature branch
4. Prepare implementation task
5. Implement
6. Review
7. Verify
8. Commit
9. Push
10. Create Pull Request
11. Merge
12. Synchronize main
13. Delete feature branch
14. Verify clean repository
15. Start the next increment in a new chat

No steps should be skipped.

---

# 6. Synchronize Repository

Before starting work:

```bash
git checkout main
git pull origin main
git status --short
```

Repository must be clean before creating a feature branch.

---

# 7. Review Roadmap

Before implementation:

Read the appropriate roadmap.

Backend:

docs/roadmap/modules-roadmap.md

Frontend UI:

docs/roadmap/ui-kit-roadmap.md

Roadmaps are authoritative.

---

# 8. Branch Naming

Feature branches:

feature/mod-XXX-short-description

Examples:

feature/mod-006-2-document-management-models

feature/ui-041-treeview-refactor

Never develop directly on main.

---

# 9. Implementation

Before coding:

* Understand the increment.
* Inspect similar existing modules.
* Follow project architecture.
* Keep implementation limited to the current increment.

Avoid unrelated refactoring.

---

# 10. Codex Rules

Codex is responsible for implementation only.

Codex must:

* inspect required files
* implement only requested work
* preserve architecture
* avoid unrelated changes

Codex must NOT:

* commit
* push
* create Pull Requests
* merge
* modify unrelated files

After implementation Codex should provide:

* implementation summary
* compile/test results
* git diff summary
* git status

---

# 11. Code Review

Review:

* architecture consistency
* naming
* imports
* typing
* documentation
* roadmap updates
* unrelated changes

---

# 12. Verification

Minimum verification:

```bash
python -m compileall backend/app
```

If Windows Python launcher fails:

```bash
backend\.venv\Scripts\python.exe -m compileall backend/app
```

When applicable:

```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests -q
```

Additional verification may include:

* ruff
* black
* mypy

when enabled by the project.

---

# 13. Documentation

Documentation is part of every increment.

Whenever required:

* update roadmap
* update architecture docs
* update README
* update developer documentation

Documentation should be committed together with code.

---

# 14. Commit Rules

After successful verification:

```bash
git add .
git commit -m "<message>"
```

Commit message must be:

* short
* descriptive
* imperative

Examples:

Add document management architecture skeleton

Add user management repository tests

Complete organization module stabilization

---

# 15. Push Rules

Always push the feature branch.

```bash
git push -u origin <feature-branch>
```

---

# 16. Pull Request Rules

Create one Pull Request per increment.

PR title should match the increment.

PR description should include:

* increment ID
* summary
* verification results

---

# 17. Merge Rules

After approval:

Merge into main.

No additional work should be added during merge.

---

# 18. Cleanup

After merge:

```bash
git checkout main
git pull origin main

git branch -d <feature-branch>

git push origin --delete <feature-branch>
```

Remote deletion errors caused by an already deleted branch are non-blocking.

---

# 19. Final Verification

Run:

```bash
git status --short
git log --oneline -5
```

Repository should be clean.

---

# 20. Definition of Done

An increment is complete only if:

* implementation finished
* verification passed
* documentation updated
* commit created
* branch pushed
* Pull Request created
* Pull Request merged
* local main synchronized
* feature branch removed
* repository clean

---

# 21. New Chat Rule

Every new increment starts in a new chat.

Do not continue multiple increments in one conversation.

---

# 22. Common Mistakes

Avoid:

* working on main
* skipping verification
* forgetting roadmap updates
* mixing unrelated changes
* forgetting commit
* forgetting push
* forgetting merge
* forgetting cleanup
* forgetting synchronization

---

# 23. Standard Command Sequence

```bash
git checkout main
git pull origin main

git checkout -b feature/<branch>

# implementation

python -m compileall backend/app

git add .
git commit -m "<message>"
git push -u origin <branch>

# create PR
# merge PR

git checkout main
git pull origin main

git branch -d <branch>
git push origin --delete <branch>

git status --short
```

---

# 24. Assistant Workflow

For every new increment, ChatGPT should:

1. Follow this workflow document.
2. Review the appropriate roadmap.
3. Generate a Codex-ready implementation prompt.
4. Include all required verification commands.
5. Include commit and push commands.
6. Remind about PR creation and merge.
7. Remind about post-merge cleanup.
8. End by instructing to continue the next increment in a new chat.

This workflow is the default process for all future PK SKDK development unless explicitly overridden.
