#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python -m local_alexa.cli "turn on the kitchen light"
python -m local_alexa.cli "set a timer for 12 minutes"
python -m local_alexa.cli "turn it off"
