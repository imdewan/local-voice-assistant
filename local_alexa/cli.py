from __future__ import annotations

import argparse
import sys

from .config import load_settings
from .llm_client import LLMClientError, reply_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send text to the local Gemma voice assistant.")
    parser.add_argument("text", nargs="*", help="Text to send")
    args = parser.parse_args(argv)

    text = " ".join(args.text).strip()
    if not text:
        text = input("Command: ").strip()
    if not text:
        print("No command supplied.", file=sys.stderr)
        return 2

    settings = load_settings()
    try:
        print(reply_text(text, settings))
    except (LLMClientError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
