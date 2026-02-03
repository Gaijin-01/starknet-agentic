---
name: sherpa-onnx-tts
description: Local text-to-speech via sherpa-onnx (offline, no cloud)
metadata:
  {
    "openclaw":
      {
        "emoji": "🗣️",
        "os": ["darwin", "linux", "win32"],
        "requires": { "env": ["SHERPA_ONNX_RUNTIME_DIR", "SHERPA_ONNX_MODEL_DIR"] },
        "install":
          [
            {
              "id": "download-runtime-macos",
              "kind": "download",
              "os": ["darwin"],
              "url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/v1.12.23/sherpa-onnx-v1.12.23-osx-universal2-shared.tar.bz2",
              "archive": "tar.bz2",
              "extract": true,
              "stripComponents": 1,
              "targetDir": "~/.openclaw/tools/sherpa-onnx-tts/runtime",
              "label": "Download sherpa-onnx runtime (macOS)",
            },
            {
              "id": "download-runtime-linux-x64",
              "kind": "download",
              "os": ["linux"],
              "url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/v1.12.23/sherpa-onnx-v1.12.23-linux-x64-shared.tar.bz2",
              "archive": "tar.bz2",
              "extract": true,
              "stripComponents": 1,
              "targetDir": "~/.openclaw/tools/sherpa-onnx-tts/runtime",
              "label": "Download sherpa-onnx runtime (Linux x64)",
            },
            {
              "id": "download-runtime-win-x64",
              "kind": "download",
              "os": ["win32"],
              "url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/v1.12.23/sherpa-onnx-v1.12.23-win-x64-shared.tar.bz2",
              "archive": "tar.bz2",
              "extract": true,
              "stripComponents": 1,
              "targetDir": "~/.openclaw/tools/sherpa-onnx-tts/runtime",
              "label": "Download sherpa-onnx runtime (Windows x64)",
            },
            {
              "id": "download-model-lessac",
              "kind": "download",
              "url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-lessac-high.tar.bz2",
              "archive": "tar.bz2",
              "extract": true,
              "targetDir": "~/.openclaw/tools/sherpa-onnx-tts/models",
              "label": "Download Piper en_US lessac (high)",
            },
          ],
      },
  }
---

# sherpa-onnx-tts

## Overview

Offline text-to-speech using sherpa-onnx. Runs entirely locally with no cloud dependencies, supporting multiple platforms and voice models.

**When to use:**
- Generating speech without internet
- Privacy-sensitive TTS applications
- Fast TTS responses without API latency
- Offline voice generation
- Custom voice model support

**Key capabilities:**
- Multiple platform support (macOS, Linux, Windows)
- Various voice models available
- WAV audio output
- Low latency inference
- No API costs

## Workflow

```
1. Download runtime for your OS
2. Download a voice model
3. Configure environment variables
4. Run TTS with text input
5. Use generated WAV file
```

## Examples

**Generate speech:**
```bash
{baseDir}/bin/sherpa-onnx-tts -o ./tts.wav "Hello from local TTS."
```

**Add to PATH for convenience:**
```bash
export PATH="{baseDir}/bin:$PATH"
sherpa-onnx-tts -o greet.wav "Welcome!"
```

**Windows PowerShell:**
```powershell
node {baseDir}\\bin\\sherpa-onnx-tts -o tts.wav "Hello from Windows TTS."
```

**Custom model selection:**
```bash
SHERPA_ONNX_MODEL_DIR=/path/to/another/model ./bin/sherpa-onnx-tts -o output.wav "Different voice"
```

## Install

1. Download the runtime for your OS (extracts into `~/.openclaw/tools/sherpa-onnx-tts/runtime`)
2. Download a voice model (extracts into `~/.openclaw/tools/sherpa-onnx-tts/models`)

Update `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "sherpa-onnx-tts": {
        env: {
          SHERPA_ONNX_RUNTIME_DIR: "~/.openclaw/tools/sherpa-onnx-tts/runtime",
          SHERPA_ONNX_MODEL_DIR: "~/.openclaw/tools/sherpa-onnx-tts/models/vits-piper-en_US-lessac-high",
        },
      },
    },
  },
}
```

The wrapper lives in this skill folder. Run it directly, or add the wrapper to PATH:

```bash
export PATH="{baseDir}/bin:$PATH"
```

## Usage

```bash
{baseDir}/bin/sherpa-onnx-tts -o ./tts.wav "Hello from local TTS."
```

Notes:

- Pick a different model from the sherpa-onnx `tts-models` release if you want another voice.
- If the model dir has multiple `.onnx` files, set `SHERPA_ONNX_MODEL_FILE` or pass `--model-file`.
- You can also pass `--tokens-file` or `--data-dir` to override the defaults.
- Windows: run `node {baseDir}\\bin\\sherpa-onnx-tts -o tts.wav "Hello from local TTS."`
