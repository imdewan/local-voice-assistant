from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import queue
import time

import numpy as np


DEFAULT_WAKE_MODEL = "hey_jarvis"


@dataclass(frozen=True)
class WakeResult:
    label: str
    score: float


class OpenWakeWordDetector:
    def __init__(
        self,
        wake_model: str | Path = DEFAULT_WAKE_MODEL,
        *,
        threshold: float = 0.5,
        inference_framework: str = "onnx",
        vad_threshold: float = 0.0,
    ):
        try:
            from openwakeword.model import Model
        except ImportError as exc:
            raise RuntimeError("openwakeword is required for wake word detection. Install requirements-pi.txt.") from exc

        self.threshold = threshold
        self.model_name = str(wake_model)
        model_ref = _resolve_wake_model(wake_model)
        self.model = Model(
            wakeword_models=[str(model_ref)],
            inference_framework=inference_framework,
            vad_threshold=vad_threshold,
        )

    def wait_for_wake(
        self,
        *,
        device: int | str | None = None,
        sample_rate: int = 16000,
        frame_ms: int = 80,
        timeout_seconds: float | None = None,
    ) -> WakeResult | None:
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise RuntimeError("sounddevice is required for wake word detection. Install requirements-pi.txt.") from exc

        frame_samples = int(sample_rate * frame_ms / 1000)
        audio_queue: queue.Queue[bytes] = queue.Queue()
        started = time.monotonic()

        def callback(indata, _frames, _time, status):
            if status:
                pass
            audio_queue.put(bytes(indata))

        with sd.RawInputStream(
            samplerate=sample_rate,
            blocksize=frame_samples,
            channels=1,
            dtype="int16",
            callback=callback,
            device=device,
        ):
            while True:
                if timeout_seconds is not None and time.monotonic() - started > timeout_seconds:
                    return None
                try:
                    chunk = audio_queue.get(timeout=0.25)
                except queue.Empty:
                    continue

                scores = self.model.predict(np.frombuffer(chunk, dtype=np.int16))
                label, score = _best_score(scores)
                if score >= self.threshold:
                    self.model.reset()
                    return WakeResult(label=label, score=score)


def _resolve_wake_model(wake_model: str | Path) -> str | Path:
    path = Path(wake_model)
    if path.exists():
        return path
    return str(wake_model)


def _best_score(scores: dict[str, float]) -> tuple[str, float]:
    if not scores:
        return "", 0.0
    label, score = max(scores.items(), key=lambda item: float(item[1]))
    return label, float(score)
