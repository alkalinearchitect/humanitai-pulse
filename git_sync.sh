#!/usr/bin/env bash
# git_sync.sh — safe commit+push for HumanitAI Pulse crons.
# Usage: git_sync.sh "commit message"
# Does: add -> commit -> rebase-pull -> push, with hard exit-code checks
# so a non-fast-forward rejection is reported (not silently swallowed).
set -u
MSG="${1:-auto: humanitai-pulse update}"
cd "$(dirname "$0")/.." || exit 1   # repo root (script lives in a subfolder or root)

# Stage + commit only if there is something to commit
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "$MSG" || { echo "GIT_SYNC_FAIL: commit failed"; exit 1; }
else
  echo "GIT_SYNC: nothing to commit"
fi

# Rebase-pull to avoid non-fast-forward rejection
git pull --rebase origin main || { echo "GIT_SYNC_FAIL: rebase-pull failed (resolve conflict manually)"; exit 2; }

# Push with checked exit code (NOT -q so errors are visible)
if git push origin main; then
  echo "GIT_SYNC_OK: pushed"
  exit 0
else
  echo "GIT_SYNC_FAIL: push rejected even after rebase — remote moved again"
  exit 3
fi
