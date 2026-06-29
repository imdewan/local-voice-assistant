#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p vendor
if [ ! -d vendor/whisper.cpp/.git ]; then
  git clone https://github.com/ggml-org/whisper.cpp vendor/whisper.cpp
else
  git -C vendor/whisper.cpp pull --ff-only
fi

cmake -S vendor/whisper.cpp -B vendor/whisper.cpp/build -DCMAKE_BUILD_TYPE=Release
JOBS="${JOBS:-1}"
cmake --build vendor/whisper.cpp/build --config Release -j"$JOBS" --target whisper-cli

echo "Built whisper.cpp at vendor/whisper.cpp/build/bin/whisper-cli"
