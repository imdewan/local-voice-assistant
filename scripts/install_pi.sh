#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"

sudo apt update
sudo apt install -y \
  git \
  curl \
  build-essential \
  cmake \
  python3 \
  python3-venv \
  python3-pip \
  alsa-utils \
  ffmpeg \
  sox

"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10+ is required for KittenTTS dependencies.")
PY

"$PYTHON" -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements-pi.txt

echo "Pi dependencies installed."
