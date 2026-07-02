#!/usr/bin/env bash
set -euo pipefail

git switch main
git pull origin main

echo
echo "Current branch:"
git branch --show-current

echo
echo "Status:"
git status
