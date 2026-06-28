#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p vendor
if [ ! -d vendor/llama.cpp/.git ]; then
  git clone https://github.com/ggml-org/llama.cpp vendor/llama.cpp
else
  git -C vendor/llama.cpp pull --ff-only
fi

cmake -S vendor/llama.cpp -B vendor/llama.cpp/build -DCMAKE_BUILD_TYPE=Release
cmake --build vendor/llama.cpp/build --config Release -j"$(getconf _NPROCESSORS_ONLN)" --target llama-server llama-cli

echo "Built llama.cpp at vendor/llama.cpp/build/bin"

