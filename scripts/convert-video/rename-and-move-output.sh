#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob

mkdir -p output

for inner_output in */output; do
  parent=${inner_output%/output}
  [[ $parent == output ]] && continue
  mv -T "$inner_output" "output/${parent%/}"
done
