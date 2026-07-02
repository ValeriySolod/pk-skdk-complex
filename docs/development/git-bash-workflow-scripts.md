# Git Bash Workflow Scripts

## Purpose

The `scripts/` directory contains small Git Bash helpers for common development workflows in the PK SKDK project. They keep branch setup, finish checks, and local cleanup consistent without committing or pushing changes automatically.

## Scripts

### `scripts/git-sync-main.sh`

Switches to `main`, pulls the latest changes from `origin main`, then prints the current branch and full Git status.

Usage:

```bash
./scripts/git-sync-main.sh
```

### `scripts/git-start-feature.sh`

Creates a new feature branch from an up-to-date `main`.

Usage:

```bash
./scripts/git-start-feature.sh feature/dev-001-git-bash-workflow-scripts
```

The script requires exactly one argument: the new branch name. It switches to `main`, pulls from `origin main`, creates the branch, then prints the current branch and full Git status.

### `scripts/git-finish-feature.sh`

Runs local finish checks for the currently checked out branch.

Usage:

```bash
./scripts/git-finish-feature.sh
```

The script prints the current branch, runs `git status --short`, runs `git diff --check`, and shows next-step hints for `git add`, `git commit`, and `git push`.

### `scripts/git-clean-merged-branches.sh`

Removes local branches that have already been merged into `main`.

Usage:

```bash
./scripts/git-clean-merged-branches.sh
```

The script switches to `main`, pulls from `origin main`, lists merged local branches, and deletes eligible branches with `git branch -d`.

## Safety Notes

- The scripts use `set -euo pipefail` so failures stop execution.
- `git-finish-feature.sh` never stages, commits, or pushes changes.
- `git-clean-merged-branches.sh` never deletes `main`.
- `git-clean-merged-branches.sh` switches to `main` before cleanup, so the current branch after the switch is protected as well.
- Branch cleanup uses `git branch -d`, which refuses to delete branches that Git does not consider safely merged.

## Recommended Workflow

Start a task from the latest `main`:

```bash
./scripts/git-start-feature.sh feature/my-task
```

Work normally, then run finish checks:

```bash
./scripts/git-finish-feature.sh
```

Review the output, then stage, commit, and push manually:

```bash
git add <files>
git commit -m "Describe the completed task"
git push -u origin feature/my-task
```

After the branch is merged, clean up merged local branches:

```bash
./scripts/git-clean-merged-branches.sh
```
