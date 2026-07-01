#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -d .venv ]; then
  . .venv/bin/activate
fi

python - <<'PY'
from pathlib import Path

import openwakeword
import openwakeword.utils

if hasattr(openwakeword.utils, "download_models"):
    openwakeword.utils.download_models()
    print("Downloaded openWakeWord built-in models.")
else:
    models_dir = Path(openwakeword.__file__).resolve().parent / "resources" / "models"
    required = models_dir / "hey_jarvis_v0.1.onnx"
    if not required.exists():
        raise SystemExit(f"openWakeWord bundled model not found: {required}")
    print(f"openWakeWord models are bundled at {models_dir}")
PY
