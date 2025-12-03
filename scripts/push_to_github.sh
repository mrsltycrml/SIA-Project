#!/usr/bin/env bash
# Automate git init / commit / push to GitHub (POSIX)
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v git >/dev/null 2>&1; then
  echo "git is not installed. Install git and re-run."
  exit 1
fi

REPO_URL=${1:-}
CREATE_REPO=${2:-false}
REPO_NAME=${3:-}
PRIVATE=${4:-false}

if [ ! -d .git ]; then
  git init
  git branch -M main
fi

if [ -n "$(git status --porcelain)" ]; then
  git add .
  git commit -m "Initial commit: Entertainment system"
else
  echo "No changes to commit."
fi

if [ "$CREATE_REPO" = "true" ] && command -v gh >/dev/null 2>&1; then
  if [ -z "$REPO_NAME" ]; then
    read -p "Repo name (e.g. SIA-Project): " REPO_NAME
  fi
  PRIV_FLAG="--public"
  if [ "$PRIVATE" = "true" ]; then
    PRIV_FLAG="--private"
  fi
  gh repo create "$REPO_NAME" $PRIV_FLAG --source=. --remote=origin --push --confirm
  exit 0
fi

if [ -z "$REPO_URL" ]; then
  read -p "Enter GitHub repo HTTPS URL (e.g. https://github.com/USER/REPO.git): " REPO_URL
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote remove origin
fi
git remote add origin "$REPO_URL"

git push -u origin main
echo "Push succeeded."


