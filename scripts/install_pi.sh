#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-$(command -v python3.11 || command -v python3.12 || command -v python3.10 || command -v python3)}"

sudo apt update
sudo apt install -y \
  git \
  curl \
  build-essential \
  cmake \
  python3 \
  python3-venv \
  python3-pip \
  libportaudio2 \
  portaudio19-dev \
  alsa-utils \
  ffmpeg \
  sox

"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 10) or sys.version_info >= (3, 13):
    raise SystemExit("Python 3.10, 3.11, or 3.12 is required. KittenTTS/misaki does not support this Python.")
PY

"$PYTHON" -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements-pi.txt

echo "Pi dependencies installed."
