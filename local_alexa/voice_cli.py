from __future__ import annotations

import argparse
import json
import sys

from .config import load_settings
from .stt_whisper_cpp import DEFAULT_WHISPER_MODEL_PATH
from .tts_kittentts import DEFAULT_KITTEN_MODEL, DEFAULT_KITTEN_SPEED, DEFAULT_KITTEN_VOICE, KittenSpeaker
from .voice_assistant import listen_route_speak, run_live_loop
from .wake_openwakeword import DEFAULT_WAKE_MODEL


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one local voice assistant turn.")
    parser.add_argument("--whisper-model", default=str(DEFAULT_WHISPER_MODEL_PATH))
    parser.add_argument("--kitten-model", default=DEFAULT_KITTEN_MODEL)
    parser.add_argument("--voice", default=DEFAULT_KITTEN_VOICE)
    parser.add_argument("--speed", type=float, default=DEFAULT_KITTEN_SPEED)
    parser.add_argument("--record-seconds", type=float, default=None)
    parser.add_argument("--max-seconds", type=float, default=8.0)
    parser.add_argument("--follow-up-seconds", type=float, default=3.0)
    parser.add_argument("--no-playback", action="store_true")
    parser.add_argument("--work-dir", default=None)
    parser.add_argument("--input-wav", default=None, help="Use an existing WAV instead of recording.")
    parser.add_argument("--input-device", default=None, help="sounddevice input device id or name.")
    parser.add_argument("--output-device", default=None, help="sounddevice output device id or name.")
    parser.add_argument("--loop", action="store_true", help="Run continuously until you say stop/quit/exit.")
    parser.add_argument("--no-wake-word", action="store_true", help="Skip wake word and listen for commands continuously.")
    parser.add_argument("--wake-model", default=DEFAULT_WAKE_MODEL, help="openWakeWord model name or model path.")
    parser.add_argument("--wake-threshold", type=float, default=0.5)
    parser.add_argument("--speak", default=None, help="Synthesize text directly with KittenTTS and skip STT/LLM.")
    args = parser.parse_args(argv)

    try:
        if args.speak is not None:
            speaker = KittenSpeaker(model_name=args.kitten_model, voice=args.voice, speed=args.speed)
            path = speaker.synthesize_to_file(args.speak)
            print(json.dumps({"reply_wav": str(path)}))
            return 0

        if args.loop:
            run_live_loop(
                settings=load_settings(),
                whisper_model_path=args.whisper_model,
                kitten_model=args.kitten_model,
                kitten_voice=args.voice,
                kitten_speed=args.speed,
                record_seconds=args.record_seconds,
                max_seconds=args.max_seconds,
                follow_up_seconds=args.follow_up_seconds,
                no_playback=args.no_playback,
                work_dir=args.work_dir,
                input_device=_coerce_device(args.input_device),
                output_device=_coerce_device(args.output_device),
                no_wake_word=args.no_wake_word,
                wake_model=args.wake_model,
                wake_threshold=args.wake_threshold,
            )
            return 0

        result = listen_route_speak(
            settings=load_settings(),
            whisper_model_path=args.whisper_model,
            kitten_model=args.kitten_model,
            kitten_voice=args.voice,
            kitten_speed=args.speed,
            record_seconds=args.record_seconds,
            max_seconds=args.max_seconds,
            no_playback=args.no_playback,
            work_dir=args.work_dir,
            input_wav_path=args.input_wav,
            input_device=_coerce_device(args.input_device),
            output_device=_coerce_device(args.output_device),
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "transcript": result.transcript,
                "reply": result.reply,
                "reply_wav": str(result.reply_wav),
                "elapsed_seconds": round(result.elapsed_seconds, 3),
            },
            indent=2,
        )
    )
    return 0


def _coerce_device(device: str | None) -> int | str | None:
    if device is None or device == "":
        return None
    try:
        return int(device)
    except ValueError:
        return device

if __name__ == "__main__":
    raise SystemExit(main())
