#!/usr/bin/env bash
set -euo pipefail

EMAIL_TO="sunmingtao@gmail.com"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/output"
DEST_DIR="/mnt/usb"

if [[ -z "${TMUX:-}" ]]; then
  printf 'Run this script inside a tmux session.\n' >&2
  exit 1
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  printf 'Source directory does not exist: %s\n' "$SOURCE_DIR" >&2
  exit 1
fi

if [[ ! -d "$DEST_DIR" ]] || ! mountpoint -q "$DEST_DIR"; then
  printf 'USB destination is not mounted at %s\n' "$DEST_DIR" >&2
  exit 1
fi

send_notification() {
  local subject="$1"
  local body="$2"

  if command -v mail >/dev/null 2>&1; then
    printf '%s\n' "$body" | mail -s "$subject" "$EMAIL_TO"
  elif command -v sendmail >/dev/null 2>&1; then
    {
      printf 'To: %s\n' "$EMAIL_TO"
      printf 'Subject: %s\n' "$subject"
      printf '\n%s\n' "$body"
    } | sendmail -t
  else
    printf 'No mail or sendmail command found; email notification was not sent.\n' >&2
  fi
}

rsync -a --whole-file --partial "$SOURCE_DIR"/ "$DEST_DIR"/
find "$SOURCE_DIR" -type f -delete
find "$SOURCE_DIR" -mindepth 1 -type d -empty -delete

send_notification \
  "Video transfer complete" \
  "Videos from ${SOURCE_DIR} were copied to ${DEST_DIR} and source files were deleted on $(hostname) at $(date)."
