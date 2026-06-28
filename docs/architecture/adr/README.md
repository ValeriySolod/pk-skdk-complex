# Architecture Decision Records

Architecture Decision Records (ADRs) document significant architectural decisions made for this project. Each ADR captures the context for a decision, the decision itself, and the consequences of adopting it so future contributors can understand why the project is structured the way it is.

## When to create an ADR

Create an ADR when a decision has a meaningful impact on the architecture, development workflow, maintainability, or long-term direction of the project. Examples include decisions about project structure, shared module ownership, technology choices, cross-cutting conventions, or patterns that multiple contributors must follow.

An ADR is not required for small implementation details, routine bug fixes, or changes that are unlikely to affect future design decisions.

## Naming convention

ADR files use the following naming convention:

```text
ADR-###-short-kebab-case-title.md
```

- `###` is a zero-padded sequential number.
- `short-kebab-case-title` briefly describes the decision.
- The file extension is `.md`.

Example:

```text
ADR-001-shared-ui.md
```

## Status values

ADRs use one of the following status values:

- **Proposed**: The decision is under consideration and has not yet been adopted.
- **Accepted**: The decision has been approved and should be followed.
- **Superseded**: The decision has been replaced by a newer ADR.

## Recommended ADR structure

Each ADR should use this structure:

```markdown
# ADR-###: Title

## Status

Proposed | Accepted | Superseded

## Context

Describe the situation, constraints, and forces that led to the decision.

## Decision

Describe the decision clearly and specifically.

## Consequences

Describe the expected benefits, trade-offs, and follow-up work.
```
