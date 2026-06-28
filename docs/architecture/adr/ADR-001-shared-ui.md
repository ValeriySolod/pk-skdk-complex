# ADR-001: Shared UI Component Location and Standards

## Status

Accepted

## Context

The project needs a single, predictable location for universal UI components so contributors can reuse common building blocks without duplicating component implementations or mixing presentation concerns with business and domain behavior.

Universal UI components are intended to be generic application primitives. They should be safe to use across features and domains, easy to style consistently, and simple to discover through a stable public export surface.

Existing shared UI components include:

- `Card`
- `Button`
- `Input`
- `Select`
- `Textarea` planned or in progress

## Decision

Universal UI components must live only in:

```text
frontend/src/shared/ui
```

Shared UI components must follow these standards:

- They must not contain business or domain logic.
- They should export props interfaces so consumers can type component usage consistently.
- They should support native HTML props where appropriate.
- Styling should use CSS Modules.
- Components should be accessible by default, including appropriate semantic elements, labels, focus behavior, and ARIA attributes when needed.
- `shared/ui/index.ts` is the public barrel export for shared UI components.

## Consequences

This keeps universal UI components centralized and predictable. Contributors know where to add or find reusable UI primitives, and feature-specific or domain-specific logic remains outside the shared UI layer.

The shared UI layer stays focused on accessible, reusable presentation components. New universal components should follow the same conventions before being exported through the public barrel file.
