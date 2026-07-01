#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

sudo apt update
sudo apt install -y \
  git \
  curl \
  build-essential \
  cmake \
  libcurl4-openssl-dev \
  python3 \
  python3-venv \
  python3-pip \
  libportaudio2 \
  portaudio19-dev \
  espeak-ng \
  alsa-utils \
  ffmpeg \
  sox

. ./scripts/ensure_python_venv.sh
. .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements-pi.txt

echo "Pi dependencies installed."
