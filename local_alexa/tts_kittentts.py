from __future__ import annotations

from pathlib import Path
import tempfile


DEFAULT_KITTEN_MODEL = "KittenML/kitten-tts-nano-0.8"
DEFAULT_KITTEN_VOICE = "expr-voice-5-m"
DEFAULT_KITTEN_SPEED = 1.3


class KittenSpeaker:
    def __init__(
        self,
        *,
        model_name: str = DEFAULT_KITTEN_MODEL,
        voice: str = DEFAULT_KITTEN_VOICE,
        speed: float = DEFAULT_KITTEN_SPEED,
    ):
        try:
            from kittentts import KittenTTS
        except ImportError as exc:
            raise RuntimeError(
                "kittentts is required for speech output. Run ./scripts/install_kittentts.sh."
            ) from exc

        self.model_name = model_name
        self.voice = voice
        self.speed = speed
        self.model = KittenTTS(model_name)

    def synthesize_to_file(self, text: str, output_path: str | Path | None = None) -> Path:
        if output_path is None:
            output_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.model.generate_to_file(text, str(path), voice=self.voice, speed=self.speed)
        return path
