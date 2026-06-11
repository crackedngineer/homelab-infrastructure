#!/bin/bash

set -e

REPO_URL="https://github.com/crackedngineer/homelab-infrastructure.git"
BRANCH="master"
SPARSE_PATH="traefik"
WORKDIR="/tmp/traefik-repo"
TARGET_DIR="/etc/traefik"
BACKUP_DIR="/etc/traefik.bak.$(date +%s)"

echo "🚀 Starting Traefik config update..."

# Step 1: Clone or update repo with sparse checkout
if [ ! -d "$WORKDIR/.git" ]; then
  echo "📥 Cloning repo with sparse checkout..."
  git clone --depth=1 --filter=blob:none --sparse -b "$BRANCH" "$REPO_URL" "$WORKDIR"
  cd "$WORKDIR"
  git sparse-checkout set "$SPARSE_PATH"
else
  echo "🔄 Updating existing repo..."
  cd "$WORKDIR"
  git fetch origin "$BRANCH"
  git reset --hard "origin/$BRANCH"
  git sparse-checkout set "$SPARSE_PATH"
fi

# Step 2: Validate folder exists
if [ ! -d "$WORKDIR/$SPARSE_PATH" ]; then
  echo "❌ ERROR: $SPARSE_PATH not found in repo"
  exit 1
fi

# Step 3: Backup existing Traefik config
if [ -d "$TARGET_DIR" ]; then
  echo "💾 Backing up current config to $BACKUP_DIR"
  cp -r "$TARGET_DIR" "$BACKUP_DIR"
fi

# Step 4: Replace config
echo "📂 Replacing /etc/traefik..."
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"
cp -r "$WORKDIR/$SPARSE_PATH/"* "$TARGET_DIR/"

# Step 5: Set permissions (optional)
chown -R root:root "$TARGET_DIR"

# Step 6: Restart Traefik service
if command -v systemctl &>/dev/null && systemctl is-active --quiet traefik; then
  echo "🔄 Restarting Traefik (systemd)..."
  systemctl restart traefik
elif command -v rc-service &>/dev/null && rc-service traefik status &>/dev/null; then
  echo "🔄 Restarting Traefik (OpenRC)..."
  rc-service traefik restart
else
  echo "ℹ️ Traefik service not active — skipping restart"
fi

echo "✅ Traefik config updated successfully!"