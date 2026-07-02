#!/usr/bin/env bash
set -euo pipefail

echo "Current branch:"
git branch --show-current

echo
echo "Short status:"
git status --short

echo
echo "Whitespace check:"
git diff --check

cat <<'EOF'

Next steps:
  git add <files>
  git commit -m "Describe the completed task"
  git push -u origin <current-branch>

This script does not add, commit, or push automatically.
EOF
