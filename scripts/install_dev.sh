#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

. ./scripts/ensure_python_venv.sh
. .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements-pi.txt
python -m pip install \
  huggingface_hub \
  num2words \
  espeakng_loader \
  misaki \
  addict \
  regex \
  spacy \
  phonemizer-fork
python -m pip install --no-deps "https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl"

echo "Installed local dev/runtime dependencies into .venv"
