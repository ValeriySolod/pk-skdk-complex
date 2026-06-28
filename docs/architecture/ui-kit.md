# UI Kit

## Source of truth

Reusable UI components are stored only in:

`frontend/src/shared/ui`

Do not create new universal UI components in `shared/components`.

## Rules

- One component = one folder.
- Each component has:
  - `Component.tsx`
  - `Component.module.css`
  - `index.ts`
- Components use TypeScript.
- Components use CSS Modules.
- Components must not contain business logic.
- Components must not depend on modules.
- Components must be exported from `shared/ui/index.ts`.

## Current components

- Button
- Card
- PageHeader
- SearchBox
- Loader
- EmptyState

## Planned components

- Input
- Select
- Badge
- Panel
- DataTable
- FormField