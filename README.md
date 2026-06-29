# Local Voice Assistant

A small fully local voice assistant for Raspberry Pi 3B+ experiments.

Default runtime path:

```text
Default microphone
  -> openWakeWord built-in wake model ("hey jarvis")
  -> wake tone
  -> whisper.cpp tiny.en command transcription
  -> llama.cpp server running Gemma 3 270M
  -> KittenTTS nano reply
  -> default speaker
  -> sleep tone
```

There is no startup greeting, no Vosk path, and no JSON command router. The assistant records only after wake, sends the transcript to Gemma, speaks the reply, then goes back to sleep.

## Models

- LLM: `bartowski/google_gemma-3-270m-it-GGUF:Q4_K_M`
- STT: `ggerganov/whisper.cpp` `ggml-tiny.en.bin`
- Wake word: openWakeWord built-in `hey_jarvis`
- TTS: `KittenML/kitten-tts-nano-0.8` at speed `1.3`

## Raspberry Pi Setup

```bash
git clone <this-project-url> local-voice-assistant
cd local-voice-assistant
./scripts/install_pi.sh
./scripts/install_kittentts.sh
./scripts/download_llama_cpp.sh
./scripts/download_whisper_cpp.sh
./scripts/download_whisper_tiny_en.sh
./scripts/download_openwakeword_models.sh
```

The Pi setup does not need npm. If something asks for npm, it is not part of this assistant path.

Use Raspberry Pi OS 64-bit with Python 3.10, 3.11, or 3.12. Raspberry Pi OS Bookworm's Python 3.11 is the best target. Python 3.13 currently breaks KittenTTS/misaki installs.

Start Gemma in terminal 1:

```bash
./scripts/run_gemma_server.sh
```

Start the live assistant in terminal 2:

```bash
./scripts/run_voice_loop.sh --work-dir work/live-assistant
```

Say `hey jarvis`, wait for the wake tone, then say one command. After it answers, it listens briefly for a follow-up without requiring the wake word again. If there is no follow-up, it plays the sleep tone and returns to idle. Say `stop`, `quit`, `exit`, `goodbye`, or `bye` as a command to end the loop.

## Debugging

Skip wake detection and immediately record commands:

```bash
./scripts/run_voice_loop.sh --no-wake-word --work-dir work/live-assistant
```

Use a different built-in openWakeWord model:

```bash
./scripts/run_voice_loop.sh --wake-model alexa --work-dir work/live-assistant
```

Tune the follow-up window:

```bash
./scripts/run_voice_loop.sh --follow-up-seconds 4 --work-dir work/live-assistant
```

Use explicit audio devices:

```bash
./scripts/run_voice_loop.sh --input-device 2 --output-device 3
```

List audio devices:

```bash
source .venv/bin/activate
python - <<'PY'
import sounddevice as sd
print(sd.query_devices())
print("default:", sd.default.device)
PY
```

## macOS/Linux Dev Setup

```bash
./scripts/install_dev.sh
./scripts/download_whisper_tiny_en.sh
./scripts/download_openwakeword_models.sh
brew install llama.cpp whisper-cpp
```

Start Gemma:

```bash
./scripts/run_gemma_server.sh
```

Text-only Gemma test:

```bash
source .venv/bin/activate
python -m local_alexa.cli "what can you do?"
```

Whisper-only WAV test:

```bash
source .venv/bin/activate
python - <<'PY'
from local_alexa.stt_whisper_cpp import WhisperCppSTT
print(WhisperCppSTT().transcribe_wav("work/live-run/input-command.wav"))
PY
```

KittenTTS-only test:

```bash
./scripts/run_voice_once.sh --speak "Hello, I am running locally with Kitten TTS."
```

## Environment

Copy `.env.example` to `.env` if you want shell defaults:

```bash
cp .env.example .env
```

Variables:

- `LOCAL_ALEXA_LLM_BASE_URL`, default `http://127.0.0.1:8080/v1`
- `LOCAL_ALEXA_MODEL`, default `bartowski/google_gemma-3-270m-it-GGUF:Q4_K_M`
- `LOCAL_ALEXA_TIMEOUT_SECONDS`, default `60`
- `LOCAL_ALEXA_KITTEN_MODEL`, default `KittenML/kitten-tts-nano-0.8`
- `LOCAL_ALEXA_KITTEN_VOICE`, default `expr-voice-5-m`

## Pi Performance Target

- Gemma context: `512` or `1024`
- Gemma output: `64` to `80` tokens
- llama.cpp threads: `4`
- Wake detector: one openWakeWord model
- STT: Whisper tiny.en only after wake

Use `./scripts/download_llama_cpp.sh` on the Pi. `./scripts/build_llama_cpp.sh` is kept as a fallback, but it uses one build job by default because parallel C++ compilation can run the Pi 3B+ out of RAM.

If Gemma is too slow on the Pi, keep the Pi as the mic/speaker satellite and run the llama.cpp server on a stronger local LAN machine.
