#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

MODEL_REF="${LOCAL_ALEXA_MODEL:-bartowski/google_gemma-3-270m-it-GGUF:Q4_K_M}"
PORT="${LOCAL_ALEXA_LLM_PORT:-8080}"
THREADS="${LOCAL_ALEXA_THREADS:-4}"
CONTEXT="${LOCAL_ALEXA_CONTEXT:-1024}"

if command -v llama-server >/dev/null 2>&1; then
  exec llama-server -hf "$MODEL_REF" -t "$THREADS" -c "$CONTEXT" --port "$PORT"
fi

LLAMA_SERVER="./vendor/llama.cpp/build/bin/llama-server"
if [ -x "$LLAMA_SERVER" ]; then
  exec "$LLAMA_SERVER" -hf "$MODEL_REF" -t "$THREADS" -c "$CONTEXT" --port "$PORT"
fi

PREBUILT_LLAMA_SERVER="$(find ./vendor/llama.cpp-prebuilt -type f -name llama-server -perm -111 2>/dev/null | head -n 1)"
if [ -n "$PREBUILT_LLAMA_SERVER" ]; then
  if ! "$PREBUILT_LLAMA_SERVER" --version >/dev/null 2>vendor/downloads/llama_cpp_prebuilt_error.txt; then
    echo "Found a prebuilt llama-server, but it is not compatible with this OS." >&2
    echo "Run ./scripts/enable_build_swap.sh and ./scripts/build_llama_cpp.sh instead." >&2
    exit 1
  fi
  exec "$PREBUILT_LLAMA_SERVER" -hf "$MODEL_REF" -t "$THREADS" -c "$CONTEXT" --port "$PORT"
fi

echo "llama-server not found. Run ./scripts/enable_build_swap.sh and ./scripts/build_llama_cpp.sh first." >&2
exit 1
