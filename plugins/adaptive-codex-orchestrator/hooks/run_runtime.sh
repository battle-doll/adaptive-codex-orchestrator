#!/bin/sh
set -eu

runtime_path="${PLUGIN_ROOT}/hooks/runtime.py"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$runtime_path"
fi
if command -v python >/dev/null 2>&1; then
  exec python "$runtime_path"
fi

exit 0
