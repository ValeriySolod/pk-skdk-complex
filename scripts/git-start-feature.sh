#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z "${1// }" ]]; then
  echo "Usage: $0 <branch-name>"
  echo "Example: $0 feature/dev-001-git-bash-workflow-scripts"
  exit 1
fi

branch_name="$1"

git switch main
git pull origin main
git switch -c "$branch_name"

echo
echo "Current branch:"
git branch --show-current

echo
echo "Status:"
git status
