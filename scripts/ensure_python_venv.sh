#!/usr/bin/env bash
set -euo pipefail

if [ -n "${BASH_SOURCE:-}" ] && [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Source this script from an installer: . ./scripts/ensure_python_venv.sh" >&2
  exit 1
fi

is_supported_python() {
  "$1" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 13) else 1)
PY
}

find_supported_python() {
  if [ -n "${PYTHON:-}" ] && command -v "$PYTHON" >/dev/null 2>&1 && is_supported_python "$PYTHON"; then
    command -v "$PYTHON"
    return 0
  fi

  local candidate
  for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && is_supported_python "$candidate"; then
      command -v "$candidate"
      return 0
    fi
  done
  return 1
}

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    UV_BIN="$(command -v uv)"
    return
  fi
  if [ -x "$HOME/.local/bin/uv" ]; then
    UV_BIN="$HOME/.local/bin/uv"
    return
  fi
  curl -LsSf https://astral.sh/uv/install.sh | sh
  UV_BIN="$HOME/.local/bin/uv"
}

if [ -x .venv/bin/python ] && ! is_supported_python .venv/bin/python; then
  echo "Removing incompatible .venv; KittenTTS needs Python 3.10, 3.11, or 3.12."
  rm -rf .venv
fi

if [ -d .venv ]; then
  . .venv/bin/activate
else
  if PYTHON_BIN="$(find_supported_python)"; then
    "$PYTHON_BIN" -m venv .venv
  else
    echo "No supported system Python found. Installing Python 3.12 with uv."
    ensure_uv
    "$UV_BIN" python install 3.12
    "$UV_BIN" venv --python 3.12 --seed .venv
  fi
  . .venv/bin/activate
fi

python - <<'PY'
import sys
if sys.version_info < (3, 10) or sys.version_info >= (3, 13):
    raise SystemExit("Python 3.10, 3.11, or 3.12 is required for KittenTTS/misaki.")
print(f"Using Python {sys.version.split()[0]} in .venv")
PY
