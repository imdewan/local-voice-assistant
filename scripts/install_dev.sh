#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-$(command -v python3.11 || command -v python3.12 || command -v python3.10 || command -v python3)}"
"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 10) or sys.version_info >= (3, 13):
    raise SystemExit("Python 3.10, 3.11, or 3.12 is required. KittenTTS/misaki does not support this Python.")
PY

if [ ! -d .venv ]; then
  "$PYTHON" -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements-pi.txt
python -m pip install "https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl"

echo "Installed local dev/runtime dependencies into .venv"
