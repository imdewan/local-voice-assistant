#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

REPO="ggml-org/whisper.cpp"
ARCH="$(uname -m)"
case "$ARCH" in
  aarch64|arm64) ASSET_NAME="whisper-bin-ubuntu-arm64.tar.gz" ;;
  x86_64|amd64) ASSET_NAME="whisper-bin-ubuntu-x64.tar.gz" ;;
  *) echo "Unsupported architecture for prebuilt whisper.cpp: $ARCH" >&2; exit 1 ;;
esac

mkdir -p vendor/downloads vendor/whisper.cpp-prebuilt

python3 - "$REPO" "$ASSET_NAME" > vendor/downloads/whisper_cpp_asset.txt <<'PY'
import json
import sys
import urllib.request

repo, asset_name = sys.argv[1], sys.argv[2]
with urllib.request.urlopen(f"https://api.github.com/repos/{repo}/releases/latest") as response:
    release = json.load(response)
for asset in release["assets"]:
    if asset["name"] == asset_name:
        print(asset["browser_download_url"])
        break
else:
    raise SystemExit(f"No whisper.cpp release asset named {asset_name}")
PY

ASSET_URL="$(sed -n '1p' vendor/downloads/whisper_cpp_asset.txt)"
ARCHIVE="vendor/downloads/${ASSET_NAME}"

if [ ! -f "$ARCHIVE" ]; then
  curl -L "$ASSET_URL" -o "$ARCHIVE"
fi

rm -rf vendor/whisper.cpp-prebuilt
mkdir -p vendor/whisper.cpp-prebuilt
tar -xzf "$ARCHIVE" -C vendor/whisper.cpp-prebuilt

WHISPER_CLI="$(find vendor/whisper.cpp-prebuilt -type f -name whisper-cli -perm -111 | head -n 1)"
if [ -z "$WHISPER_CLI" ]; then
  echo "Downloaded whisper.cpp archive did not contain whisper-cli." >&2
  exit 1
fi

echo "Installed prebuilt whisper.cpp: $WHISPER_CLI"
