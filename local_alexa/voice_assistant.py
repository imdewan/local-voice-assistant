from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile
import time

from .audio_io import play_tone, play_wav, record_until_silence, record_wav, wav_rms
from .config import Settings, load_settings
from .llm_client import reply_text
from .stt_whisper_cpp import DEFAULT_WHISPER_MODEL_PATH, WhisperCppSTT
from .tts_kittentts import DEFAULT_KITTEN_MODEL, DEFAULT_KITTEN_SPEED, DEFAULT_KITTEN_VOICE, KittenSpeaker
from .wake_openwakeword import DEFAULT_WAKE_MODEL, OpenWakeWordDetector


STOP_WORDS = {"stop", "quit", "exit", "goodbye", "bye"}
MIN_SPEECH_RMS = 320


@dataclass(frozen=True)
class VoiceRunResult:
    transcript: str
    reply: str
    reply_wav: Path
    elapsed_seconds: float


def listen_route_speak(
    *,
    settings: Settings | None = None,
    whisper_model_path: str | Path = DEFAULT_WHISPER_MODEL_PATH,
    kitten_model: str = DEFAULT_KITTEN_MODEL,
    kitten_voice: str = DEFAULT_KITTEN_VOICE,
    kitten_speed: float = DEFAULT_KITTEN_SPEED,
    record_seconds: float | None = None,
    max_seconds: float = 8.0,
    no_playback: bool = False,
    work_dir: str | Path | None = None,
    input_wav_path: str | Path | None = None,
    input_device: int | str | None = None,
    output_device: int | str | None = None,
) -> VoiceRunResult:
    settings = settings or load_settings()
    work = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="local-voice-"))
    work.mkdir(parents=True, exist_ok=True)
    input_wav = work / "input.wav"
    reply_wav = work / "reply.wav"

    start = time.perf_counter()
    if input_wav_path is not None:
        input_wav = Path(input_wav_path)
    elif record_seconds is not None:
        record_wav(input_wav, seconds=record_seconds, device=input_device)
    else:
        record_until_silence(input_wav, max_seconds=max_seconds, device=input_device)

    transcript = WhisperCppSTT(whisper_model_path).transcribe_wav(input_wav)
    reply = reply_text(transcript, settings) if transcript else "I did not catch that."

    speaker = KittenSpeaker(model_name=kitten_model, voice=kitten_voice, speed=kitten_speed)
    speaker.synthesize_to_file(reply, reply_wav)
    if not no_playback:
        play_wav(reply_wav, device=output_device)

    return VoiceRunResult(
        transcript=transcript,
        reply=reply,
        reply_wav=reply_wav,
        elapsed_seconds=time.perf_counter() - start,
    )


def synthesize_and_play(
    text: str,
    *,
    speaker: KittenSpeaker,
    output_device: int | str | None = None,
    output_path: str | Path | None = None,
    no_playback: bool = False,
) -> Path:
    path = speaker.synthesize_to_file(text, output_path)
    if not no_playback:
        play_wav(path, device=output_device)
    return path


def run_live_loop(
    *,
    settings: Settings | None = None,
    whisper_model_path: str | Path = DEFAULT_WHISPER_MODEL_PATH,
    kitten_model: str = DEFAULT_KITTEN_MODEL,
    kitten_voice: str = DEFAULT_KITTEN_VOICE,
    kitten_speed: float = DEFAULT_KITTEN_SPEED,
    max_seconds: float = 8.0,
    follow_up_seconds: float = 3.0,
    record_seconds: float | None = None,
    work_dir: str | Path | None = None,
    input_device: int | str | None = None,
    output_device: int | str | None = None,
    no_playback: bool = False,
    no_wake_word: bool = False,
    wake_model: str | Path = DEFAULT_WAKE_MODEL,
    wake_threshold: float = 0.5,
) -> None:
    settings = settings or load_settings()
    work = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="local-voice-loop-"))
    work.mkdir(parents=True, exist_ok=True)

    wake_detector = None if no_wake_word else OpenWakeWordDetector(wake_model, threshold=wake_threshold)
    command_stt = WhisperCppSTT(whisper_model_path)
    speaker = KittenSpeaker(model_name=kitten_model, voice=kitten_voice, speed=kitten_speed)

    turn = 0
    listen_for_follow_up = False
    while True:
        turn += 1
        input_wav = work / f"turn-{turn:04d}-input.wav"
        reply_wav = work / f"turn-{turn:04d}-reply.wav"

        if listen_for_follow_up:
            print(f"Listening briefly for follow-up, turn {turn}...", flush=True)
        else:
            print(f"Idle listening for wake word, turn {turn}...", flush=True)

        if wake_detector is not None and not listen_for_follow_up:
            wake = wake_detector.wait_for_wake(device=input_device, timeout_seconds=15.0)
            if wake is None:
                print("Idle: no wake word, staying asleep.", flush=True)
                continue
            print(f"Wake detected: {wake.label} ({wake.score:.3f})", flush=True)
            _wake_tone(output_device, no_playback)

        print("Listening for command...", flush=True)
        if record_seconds is not None:
            record_wav(input_wav, seconds=record_seconds, device=input_device)
        else:
            speech_start_timeout = follow_up_seconds if listen_for_follow_up else None
            record_until_silence(
                input_wav,
                max_seconds=max_seconds,
                speech_start_timeout=speech_start_timeout,
                device=input_device,
            )

        if wav_rms(input_wav) < MIN_SPEECH_RMS:
            if listen_for_follow_up:
                print("Follow-up: no speech, sleeping.", flush=True)
            else:
                print("Command: low/no speech, sleeping.", flush=True)
            _sleep_tone(output_device, no_playback)
            listen_for_follow_up = False
            continue

        transcript = command_stt.transcribe_wav(input_wav)
        print(f"Transcript: {transcript!r}", flush=True)
        if not transcript:
            if listen_for_follow_up:
                print("Follow-up: empty transcript, sleeping.", flush=True)
            else:
                print("Command: empty transcript, sleeping.", flush=True)
            _sleep_tone(output_device, no_playback)
            listen_for_follow_up = False
            continue
        elif _should_stop(transcript):
            synthesize_and_play(
                "Goodbye.",
                speaker=speaker,
                output_device=output_device,
                output_path=reply_wav,
                no_playback=no_playback,
            )
            return
        else:
            reply = reply_text(transcript, settings)

        print(f"Reply: {reply!r}", flush=True)
        synthesize_and_play(
            reply,
            speaker=speaker,
            output_device=output_device,
            output_path=reply_wav,
            no_playback=no_playback,
        )
        listen_for_follow_up = follow_up_seconds > 0
        if not listen_for_follow_up:
            _sleep_tone(output_device, no_playback)


def _should_stop(transcript: str) -> bool:
    words = set(transcript.lower().split())
    return bool(words & STOP_WORDS)


def _wake_tone(output_device: int | str | None, no_playback: bool) -> None:
    if no_playback:
        return
    play_tone(frequency=880.0, seconds=0.09, device=output_device)
    play_tone(frequency=1174.0, seconds=0.09, device=output_device)


def _sleep_tone(output_device: int | str | None, no_playback: bool) -> None:
    if no_playback:
        return
    play_tone(frequency=660.0, seconds=0.08, device=output_device)
    play_tone(frequency=440.0, seconds=0.10, device=output_device)
