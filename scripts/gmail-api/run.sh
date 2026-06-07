#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
LOCK_FILE="${SCRIPT_DIR}/run.lock"
TIMEOUT_DURATION="${GMAIL_AUTO_REPLY_TIMEOUT:-270s}"
KILL_AFTER="${GMAIL_AUTO_REPLY_KILL_AFTER:-30s}"

export VIRTUAL_ENV="${VENV_DIR}"
export PATH="${VENV_DIR}/bin:${PATH}"
unset PYTHONHOME

cd "${SCRIPT_DIR}"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "gmail-api auto reply is already running; exiting."
  exit 0
fi

exec timeout -k "${KILL_AFTER}" "${TIMEOUT_DURATION}" "${VENV_DIR}/bin/python" "${SCRIPT_DIR}/run.py"
