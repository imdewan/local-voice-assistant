from __future__ import annotations

import queue
import wave
from pathlib import Path
import math
import wave


def record_wav(
    output_path: str | Path,
    *,
    seconds: float = 5.0,
    sample_rate: int = 16000,
    channels: int = 1,
    device: int | str | None = None,
) -> Path:
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError("sounddevice is required for recording. Install requirements-pi.txt.") from exc

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=channels,
        dtype="int16",
        device=device,
    )
    sd.wait()

    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames.tobytes())

    return output


def record_until_silence(
    output_path: str | Path,
    *,
    max_seconds: float = 8.0,
    speech_start_timeout: float | None = None,
    sample_rate: int = 16000,
    frame_ms: int = 30,
    silence_ms: int = 900,
    aggressiveness: int = 2,
    device: int | str | None = None,
) -> Path:
    try:
        import sounddevice as sd
        import webrtcvad
    except ImportError as exc:
        raise RuntimeError("sounddevice and webrtcvad are required for VAD recording.") from exc

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    vad = webrtcvad.Vad(aggressiveness)
    frame_samples = int(sample_rate * frame_ms / 1000)
    frame_bytes = frame_samples * 2
    max_frames = int(max_seconds * 1000 / frame_ms)
    speech_start_timeout_frames = None
    if speech_start_timeout is not None:
        speech_start_timeout_frames = max(1, int(speech_start_timeout * 1000 / frame_ms))
    silence_frames_needed = max(1, int(silence_ms / frame_ms))
    audio_queue: queue.Queue[bytes] = queue.Queue()

    def callback(indata, _frames, _time, status):
        if status:
            pass
        audio_queue.put(bytes(indata))

    recorded: list[bytes] = []
    speech_seen = False
    silent_frames = 0

    with sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=frame_samples,
        channels=1,
        dtype="int16",
        callback=callback,
        device=device,
    ):
        for frame_index in range(max_frames):
            chunk = audio_queue.get()
            if len(chunk) != frame_bytes:
                continue
            recorded.append(chunk)
            is_speech = vad.is_speech(chunk, sample_rate)
            if is_speech:
                speech_seen = True
                silent_frames = 0
            elif speech_seen:
                silent_frames += 1
                if silent_frames >= silence_frames_needed:
                    break
            elif speech_start_timeout_frames is not None and frame_index >= speech_start_timeout_frames:
                break

    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(recorded))

    return output


def play_wav(path: str | Path, *, device: int | str | None = None) -> None:
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError("sounddevice and soundfile are required for playback.") from exc

    audio, sample_rate = sf.read(str(path), dtype="float32")
    sd.play(audio, sample_rate, device=device)
    sd.wait()


def wav_rms(path: str | Path) -> int:
    import audioop

    with wave.open(str(path), "rb") as wav:
        data = wav.readframes(wav.getnframes())
        if not data:
            return 0
        return audioop.rms(data, wav.getsampwidth())


def play_tone(
    *,
    frequency: float = 880.0,
    seconds: float = 0.12,
    sample_rate: int = 24000,
    volume: float = 0.18,
    device: int | str | None = None,
) -> None:
    try:
        import numpy as np
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError("numpy and sounddevice are required for tones.") from exc

    count = int(seconds * sample_rate)
    envelope = np.ones(count, dtype=np.float32)
    fade = min(count // 4, int(0.015 * sample_rate))
    if fade > 0:
        ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)
        envelope[:fade] = ramp
        envelope[-fade:] = ramp[::-1]
    wave_data = np.array(
        [math.sin(2.0 * math.pi * frequency * i / sample_rate) for i in range(count)],
        dtype=np.float32,
    )
    sd.play(volume * envelope * wave_data, sample_rate, device=device)
    sd.wait()
