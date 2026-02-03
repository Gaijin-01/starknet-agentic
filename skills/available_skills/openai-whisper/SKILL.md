---
name: openai-whisper
description: Local speech-to-text with the Whisper CLI (no API key).
homepage: https://openai.com/research/whisper
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "requires": { "bins": ["whisper"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "openai-whisper",
              "bins": ["whisper"],
              "label": "Install OpenAI Whisper (brew)",
            },
          ],
      },
  }
---

# Whisper (CLI)

## Overview

<<<<<<< HEAD
Quick start

=======
Local speech-to-text transcription using OpenAI's Whisper model. Runs entirely offline with no API key required. Ideal for transcribing audio files, podcasts, meeting recordings, or any audio content into text.

**When to use:**
- Transcribing audio files locally (mp3, m4a, wav, flac, etc.)
- Creating subtitles from video/audio
- Transcribing meeting recordings or podcasts
- Processing voice memos
- No internet/API key needed

**Key capabilities:**
- Multiple model sizes (tiny to large-v3) for speed/accuracy trade-off
- Multiple output formats (txt, srt, vtt, json)
- Translation mode (audio to English text)
- Word-level timestamps available

## Workflow

```
1. Identify audio file to transcribe
2. Choose model based on speed/accuracy needs:
   - tiny/fast → speed priority
   - medium/large → accuracy priority
3. Run whisper with appropriate options
4. Review output in chosen format
5. If needed, re-run with different model or options
```

## Examples

**Basic transcription to text:**
```bash
whisper /path/to/audio.mp3 --model medium --output_format txt --output_dir ./transcripts
```

**Create subtitles (SRT format):**
```bash
whisper /path/to/interview.m4a --task translate --output_format srt --output_dir ./subs
```

**Fast transcription (smaller model):**
```bash
whisper /path/meeting.wav --model tiny --output_format txt
```

**High accuracy transcription (larger model):**
```bash
whisper /path/podcast.mp3 --model large-v3 --output_format json --verbose False
```

**Quick start
>>>>>>> de3edc587 (chore: stage changes before v2026.2.1 update)
- `whisper /path/audio.mp3 --model medium --output_format txt --output_dir .`
- `whisper /path/audio.m4a --task translate --output_format srt`

Notes

- Models download to `~/.cache/whisper` on first run.
- `--model` defaults to `turbo` on this install.
- Use smaller models for speed, larger for accuracy.
