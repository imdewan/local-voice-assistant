#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export LOCAL_ALEXA_MODEL="${LOCAL_ALEXA_MODEL:-bartowski/google_gemma-3-270m-it-GGUF:Q4_K_M}"
exec ./scripts/run_llama_server.sh
