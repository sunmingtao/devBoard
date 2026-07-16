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

echo "$(date --iso-8601=seconds) Starting subtitle pipeline."
echo "$(date --iso-8601=seconds) Timeout: ${TIMEOUT_DURATION}; force-kill delay: ${KILL_AFTER}."

set +e
timeout \
  -k "${KILL_AFTER}" \
  "${TIMEOUT_DURATION}" \
  "${VENV_DIR}/bin/python" -u \
  "${SCRIPT_DIR}/run.py" \
  -mode single

exit_code=$?
set -e

case "${exit_code}" in
  0)
    echo "$(date --iso-8601=seconds) Subtitle pipeline completed successfully."
    ;;
  124)
    echo "$(date --iso-8601=seconds) ERROR: Subtitle pipeline exceeded ${TIMEOUT_DURATION} and was terminated." >&2
    ;;
  137)
    echo "$(date --iso-8601=seconds) ERROR: Subtitle pipeline did not stop within ${KILL_AFTER} and was force-killed with SIGKILL." >&2
    ;;
  *)
    echo "$(date --iso-8601=seconds) ERROR: Subtitle pipeline exited with code ${exit_code}." >&2
    ;;
esac

exit "${exit_code}"