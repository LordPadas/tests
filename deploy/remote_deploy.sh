#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <remote_user> <remote_host> <repo_path> [branch]"
  exit 1
fi

REMOTE_USER="$1"
REMOTE_HOST="$2"
REPO_PATH="$3"
BRANCH="${4:-main}"

LOCAL_DIR=$(pwd)

echo "[deploy] Pushing local repo to remote $REMOTE_USER@$REMOTE_HOST:$REPO_PATH (branch $BRANCH)"
rsync -avz --exclude '.git' --delete "$LOCAL_DIR/" "${REMOTE_USER}@${REMOTE_HOST}:$REPO_PATH/" || {
  echo "[deploy] RSYNC failed"; exit 2; }

echo "[deploy] Running remote deployment on $REMOTE_HOST"
ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -lc "set -euo pipefail; cd '$REPO_PATH'; git fetch --all || true; git reset --hard origin/$BRANCH || true; docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d --build"
echo "[deploy] Deployment command issued. Check remote logs for status."
