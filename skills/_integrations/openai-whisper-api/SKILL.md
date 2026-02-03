---
name: openai-whisper-api
description: Transcribe audio via OpenAI Audio Transcriptions API (Whisper).
homepage: https://platform.openai.com/docs/guides/speech-to-text
metadata:
  {
    "openclaw":
      {
        "emoji": "☁️",
        "requires": { "bins": ["curl"], "env": ["OPENAI_API_KEY"] },
        "primaryEnv": "OPENAI_API_KEY",
      },
  }
---

# OpenAI Whisper API (curl)

## Overview

Transcribe audio files using OpenAI's Whisper model via API. Cloud-based transcription with high accuracy, multiple language support, and optional output formatting.

**When to use:**
- Transcribing audio files with high accuracy
- Processing multi-speaker audio with prompts
- Generating structured JSON output for further processing
- When local Whisper CLI is not available
- Batch transcription workflows

**Key capabilities:**
- Multiple model support (whisper-1)
- Language specification
- Custom prompts for better transcription
- JSON and text output formats
- SRT/VTT subtitle generation possible

## Workflow

```
1. Set OPENAI_API_KEY environment variable
2. Prepare audio file (mp3, m4a, ogg, wav, flac)
3. Run transcription script with options
4. Review and use transcript output
```

## Examples

**Basic transcription:**
```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a
```

**With custom model and output:**
```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model whisper-1 --out /tmp/transcript.txt
```

**Specify language:**
```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language en
```

**With speaker prompts:**
```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --prompt "Speaker names: Peter, Daniel"
```

**JSON output for programmatic use:**
```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
```

## Quick start

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a
```

Defaults:

- Model: `whisper-1`
- Output: `<input>.txt`

## Useful flags

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model whisper-1 --out /tmp/transcript.txt
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language en
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --prompt "Speaker names: Peter, Daniel"
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
```

## API key

Set `OPENAI_API_KEY`, or configure it in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    "openai-whisper-api": {
      apiKey: "OPENAI_KEY_HERE",
    },
  },
}
```
