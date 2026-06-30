docs/roadmap/ui-kit-roadmap.md
# UI Kit Roadmap

## Purpose

This document defines the development roadmap of the shared UI Kit used by the ПК СКДК frontend.

Each component has a unique identifier (`UI-XXX`) that never changes after being assigned.

Rules:

- Every component is implemented in `frontend/src/shared/ui`.
- Every component has its own folder.
- Every component is exported through `shared/ui/index.ts`.
- Every task is completed using the workflow:

```
implementation
→ build
→ git diff --check
→ commit
→ push
→ merge
→ pull main
→ Vercel Production verification
```

---

# Completed

| ID | Component | Status |
|----|-----------|--------|
| UI-001 | Card | ✅ |
| UI-002 | Button | ✅ |
| UI-003 | Input | ✅ |
| UI-004 | Select | ✅ |
| UI-005 | Textarea | ✅ |
| UI-006 | FormField | ✅ |
| UI-007 | Checkbox | ✅ |
| UI-008 | Switch | ✅ |
| UI-009 | RadioGroup | ✅ |
| UI-010 | Modal | ✅ |
| UI-011 | Tabs | ✅ |
| UI-012 | Toast | ✅ |
| UI-013 | Table | ✅ |
| UI-014 | Pagination | ✅ |
| UI-015 | Badge | ✅ |
| UI-016 | Tooltip | ✅ |
| UI-017 | DropdownMenu | ✅ |
| UI-018 | Loader | ✅ |
| UI-019 | LoadingOverlay | ✅ |
| UI-020 | PageHeader | ✅ |
| UI-021 | Skeleton | ✅ |
| UI-022 | EmptyState | ✅ |
| UI-023 | Alert | ✅ |
| UI-024 | Banner | ✅ |
| UI-025 | Notification | ✅ |
| UI-026 | Breadcrumbs | ✅ |
| UI-027 | Stepper | ✅ |
| UI-028 | ProgressBar | ✅ |

---

# Planned

| ID | Component | Status |
|----|-----------|--------|
| UI-029 | Avatar | ✅ |
| UI-030 | Divider | ✅ |
| UI-031 | Accordion | ✅ |
| UI-032 | Avatar | ✅ |
| UI-033 | Universal Spacer | ✅ |
| UI-034 | Menu | ✅ |
| UI-035 | ContextMenu | ✅ |
| UI-036 | TreeView | ✅ |
| UI-037 | FileUpload | ✅|
| UI-038 | DatePicker | ✅ |
| UI-039 | Wrap | ✅ |
| UI-040 | Calendar | ✅ |
| UI-041 | Slider | ✅ |
| UI-042 | Tabs | ✅ |
| UI-043 | Tooltip | ✅ |
| UI-044 | Combobox | ✅ |
| UI-045 | MultiSelect | ✅ |
| UI-046 | Timeline | ✅ |
| UI-047 | AvatarGroup | ⬜ |
| UI-048 | Statistic | ⬜ |
| UI-049 | DataGrid | ⬜ |
| UI-050 | AppShell | ⬜ |
