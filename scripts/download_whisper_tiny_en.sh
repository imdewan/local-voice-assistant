#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p models
MODEL_PATH="models/ggml-tiny.en.bin"
if [ -f "$MODEL_PATH" ]; then
  echo "Whisper tiny.en model already exists at $MODEL_PATH"
  exit 0
fi

curl -L \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin" \
  -o "$MODEL_PATH"

echo "Downloaded Whisper tiny.en model to $MODEL_PATH"
