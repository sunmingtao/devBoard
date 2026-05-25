#!/bin/bash
set -euo pipefail

BACKUP_DIR="/var/backup/devboard/k3s-state"
TIMESTAMP=$(date +%F-%H%M%S)

sudo mkdir -p "$BACKUP_DIR"

cleanup() {
  echo "[$(date)] start k3s after backup"
  sudo systemctl start k3s
  echo "[$(date)] backup completed. $BACKUP_DIR/k3s-state-$TIMESTAMP.tar.gz"
}
trap cleanup EXIT

echo "[$(date)] stop k3s to backup state"
sudo systemctl stop k3s

sudo tar -czf "$BACKUP_DIR/k3s-state-$TIMESTAMP.tar.gz" \
/var/lib/rancher/k3s/server/db \
/var/lib/rancher/k3s/server/token