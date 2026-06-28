from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess


DEFAULT_WHISPER_MODEL_PATH = Path("models/ggml-tiny.en.bin")


class WhisperCppSTT:
    def __init__(
        self,
        model_path: str | Path = DEFAULT_WHISPER_MODEL_PATH,
        binary: str | Path | None = None,
    ):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Whisper model not found at {self.model_path}. Run ./scripts/download_whisper_tiny_en.sh."
            )
        self.binary = str(binary or _find_whisper_binary())

    def transcribe_wav(self, wav_path: str | Path) -> str:
        cmd = [
            self.binary,
            "-m",
            str(self.model_path),
            "-f",
            str(wav_path),
            "-nt",
            "-np",
            "-l",
            "en",
        ]
        completed = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return _clean_whisper_output(completed.stdout)


def _find_whisper_binary() -> Path:
    for name in ("whisper-cli", "whisper-cpp"):
        found = shutil.which(name)
        if found:
            return Path(found)
    local = Path("vendor/whisper.cpp/build/bin/whisper-cli")
    if local.exists():
        return local
    raise FileNotFoundError("whisper-cli not found. Run ./scripts/build_whisper_cpp.sh.")


def _clean_whisper_output(output: str) -> str:
    lines = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\[[^\]]+\]\s*", "", line).strip()
        if line:
            lines.append(line)
    return " ".join(lines).strip()
