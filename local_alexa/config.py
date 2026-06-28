from dataclasses import dataclass
import os


DEFAULT_MODEL = "bartowski/google_gemma-3-270m-it-GGUF:Q4_K_M"
DEFAULT_BASE_URL = "http://127.0.0.1:8080/v1"
DEFAULT_TIMEOUT_SECONDS = 60.0


@dataclass(frozen=True)
class Settings:
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS


def load_settings() -> Settings:
    timeout = os.environ.get("LOCAL_ALEXA_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))
    return Settings(
        base_url=os.environ.get("LOCAL_ALEXA_LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        model=os.environ.get("LOCAL_ALEXA_MODEL", DEFAULT_MODEL),
        timeout_seconds=float(timeout),
    )
