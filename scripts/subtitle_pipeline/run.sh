#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
LOCK_FILE="${SCRIPT_DIR}/run.lock"
TIMEOUT_DURATION="${SUBTITLE_PIPELINE_TIMEOUT:-12h}"
KILL_AFTER="${SUBTITLE_PIPELINE_KILL_AFTER:-1m}"

export VIRTUAL_ENV="${VENV_DIR}"
export PATH="${VENV_DIR}/bin:${PATH}"
unset PYTHONHOME

cd "${SCRIPT_DIR}"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "subtitle_pipeline is already running; exiting."
  exit 0
fi

exec timeout -k "${KILL_AFTER}" "${TIMEOUT_DURATION}" "${VENV_DIR}/bin/python" "${SCRIPT_DIR}/run.py" -mode single
