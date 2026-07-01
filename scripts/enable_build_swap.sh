#!/usr/bin/env bash
set -euo pipefail

SWAP_FILE="${SWAP_FILE:-/swapfile-local-voice-assistant}"
SWAP_SIZE="${SWAP_SIZE:-2G}"

if swapon --show=NAME | grep -qx "$SWAP_FILE"; then
  echo "Build swap is already enabled at $SWAP_FILE"
  exit 0
fi

if [ ! -f "$SWAP_FILE" ]; then
  sudo fallocate -l "$SWAP_SIZE" "$SWAP_FILE" || sudo dd if=/dev/zero of="$SWAP_FILE" bs=1M count=2048 status=progress
  sudo chmod 600 "$SWAP_FILE"
  sudo mkswap "$SWAP_FILE"
fi

sudo swapon "$SWAP_FILE"
echo "Enabled temporary build swap: $SWAP_FILE ($SWAP_SIZE)"
echo "Disable later with: sudo swapoff $SWAP_FILE"
