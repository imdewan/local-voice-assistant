from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import Settings


class LLMClientError(RuntimeError):
    pass


def complete_chat(user_text: str, settings: Settings) -> str:
    endpoint = f"{settings.base_url}/completions"
    payload = {
        "model": settings.model,
        "prompt": f"Answer briefly for voice.\nUser: {user_text.strip()}\nAssistant:",
        "temperature": 0.4,
        "max_tokens": 80,
        "stop": ["\nUser:", "\nAssistant:"],
        "stream": False,
    }
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer none"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMClientError(f"LLM server returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise LLMClientError(f"Could not reach LLM server at {endpoint}: {exc}") from exc

    data = json.loads(raw)
    try:
        return data["choices"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMClientError(f"Unexpected LLM response: {raw}") from exc

def reply_text(user_text: str, settings: Settings) -> str:
    text = complete_chat(user_text=user_text, settings=settings).strip()
    return _clean_reply(text)


def _clean_reply(text: str) -> str:
    if not text:
        return "Okay."
    for prefix in ("assistant:", "Assistant:"):
        if text.startswith(prefix):
            text = text[len(prefix) :].strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        text = " ".join(lines)
    text = re.sub(r"[^\x20-\x7E]+", "", text).strip()
    words = text.split()
    if len(words) > 28:
        text = " ".join(words[:28]).rstrip(".,;:") + "."
    return text
