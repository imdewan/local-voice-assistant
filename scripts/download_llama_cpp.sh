#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

REPO="ggml-org/llama.cpp"
ARCH="$(uname -m)"
case "$ARCH" in
  aarch64|arm64) ASSET_PATTERN='bin-ubuntu-arm64\.tar\.gz$' ;;
  x86_64|amd64) ASSET_PATTERN='bin-ubuntu-x64\.tar\.gz$' ;;
  *) echo "Unsupported architecture for prebuilt llama.cpp: $ARCH" >&2; exit 1 ;;
esac

mkdir -p vendor/downloads vendor/llama.cpp-prebuilt

python3 - "$REPO" "$ASSET_PATTERN" > vendor/downloads/llama_cpp_asset.txt <<'PY'
import json
import re
import sys
import urllib.request

repo, pattern = sys.argv[1], sys.argv[2]
with urllib.request.urlopen(f"https://api.github.com/repos/{repo}/releases/latest") as response:
    release = json.load(response)
for asset in release["assets"]:
    if re.search(pattern, asset["name"]):
        print(asset["name"])
        print(asset["browser_download_url"])
        break
else:
    raise SystemExit(f"No llama.cpp release asset matched {pattern}")
PY

ASSET_NAME="$(sed -n '1p' vendor/downloads/llama_cpp_asset.txt)"
ASSET_URL="$(sed -n '2p' vendor/downloads/llama_cpp_asset.txt)"
ARCHIVE="vendor/downloads/${ASSET_NAME}"

if [ ! -f "$ARCHIVE" ]; then
  curl -L "$ASSET_URL" -o "$ARCHIVE"
fi

rm -rf vendor/llama.cpp-prebuilt
mkdir -p vendor/llama.cpp-prebuilt
tar -xzf "$ARCHIVE" -C vendor/llama.cpp-prebuilt

LLAMA_SERVER="$(find vendor/llama.cpp-prebuilt -type f -name llama-server -perm -111 | head -n 1)"
if [ -z "$LLAMA_SERVER" ]; then
  echo "Downloaded llama.cpp archive did not contain llama-server." >&2
  exit 1
fi

if ! "$LLAMA_SERVER" --version >/dev/null 2>vendor/downloads/llama_cpp_prebuilt_error.txt; then
  echo "Downloaded llama.cpp prebuilt binary, but it is not compatible with this OS." >&2
  echo "Details:" >&2
  sed -n '1,12p' vendor/downloads/llama_cpp_prebuilt_error.txt >&2
  echo "" >&2
  echo "On Raspberry Pi OS Bookworm, use:" >&2
  echo "  ./scripts/enable_build_swap.sh" >&2
  echo "  ./scripts/build_llama_cpp.sh" >&2
  exit 1
fi

echo "Installed prebuilt llama.cpp: $LLAMA_SERVER"
