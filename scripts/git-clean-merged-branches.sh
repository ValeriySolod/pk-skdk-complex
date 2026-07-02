#!/usr/bin/env bash
set -euo pipefail

starting_branch="$(git branch --show-current)"

git switch main
git pull origin main

current_branch="$(git branch --show-current)"
deleted_any=false

echo
echo "Deleting local branches already merged into main:"

while IFS= read -r branch; do
  if [[ -z "$branch" || "$branch" == "main" || "$branch" == "$current_branch" || "$branch" == "$starting_branch" ]]; then
    continue
  fi

  git branch -d "$branch"
  deleted_any=true
done < <(git branch --format='%(refname:short)' --merged main)

if [[ "$deleted_any" == false ]]; then
  echo "No merged local branches to delete."
fi

echo
echo "Current branch:"
git branch --show-current

echo
echo "Status:"
git status
