#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -d .venv ]; then
  . .venv/bin/activate
fi

python - <<'PY'
import openwakeword.utils

openwakeword.utils.download_models()
print("Downloaded openWakeWord built-in models.")
PY
