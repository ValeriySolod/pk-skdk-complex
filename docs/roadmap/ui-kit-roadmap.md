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
| UI-029 | Avatar | ✅ |
| UI-030 | Divider | ✅ |
| UI-031 | Accordion | ✅ |
| UI-032 | Spacer | ✅ |
| UI-033 | Menu | ✅ |
| UI-038 | Wrap | ✅ |
| UI-039 | Calendar | ✅ |
| UI-040 | Slider | ✅ |
| UI-042 | MultiSelect | ✅ |
| UI-043 | Popover | ✅ |
| UI-044 | Timeline | ✅ |
| UI-045 | Container | ✅ |
| UI-046 | Grid | ✅ |
| UI-047 | Carousel | ✅ |
| UI-048 | Statistic | ✅ |
| UI-050 | DataGrid | ✅ |
| UI-052 | SearchBox | ✅ |
| UI-053 | Flex | ✅ |
| UI-054 | Inline | ✅ |

---

# Planned

| ID | Component | Status |
|----|-----------|--------|
| UI-034 | ContextMenu | ✅ |
| UI-035 | TreeView | ✅ |
| UI-036 | FileUpload | ✅ |
| UI-037 | DatePicker | ✅ |
| UI-041 | Combobox | ✅ |
| UI-049 | AppShell | ✅ |
| UI-051 | AvatarGroup | ✅ |
