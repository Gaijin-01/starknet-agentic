---
name: songsee
description: Generate spectrograms and feature-panel visualizations from audio with the songsee CLI.
homepage: https://github.com/steipete/songsee
metadata: {"clawdbot":{"emoji":"🌊","requires":{"bins":["songsee"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/songsee","bins":["songsee"],"label":"Install songsee (brew)"}]}}
---

# songsee

## Overview

Generate spectrograms and feature-panel visualizations from audio files. This skill provides audio analysis capabilities including spectral analysis, chroma features, tempo detection, and more.

**Key Capabilities:**
- Generate spectrograms (standard, Mel, chroma)
- Create multi-panel feature visualizations
- Extract audio features (MFCC, tempo, loudness, etc.)
- Support for time-slice extraction
- Multiple visualization styles and color palettes
- Stdin/stdout support for pipeline integration

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Songsee Workflow                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Input Processing                                        │
│     - Supported: WAV, MP3 (native)                          │
│     - Others: ffmpeg fallback                               │
│     - Stdin support for pipeline                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Visualization Type                                      │
│     ┌────────────┬────────────────────────────────────┐    │
│     │ Standard   │ Basic spectrogram                  │    │
│     │ Mel        │ Mel-spectrogram (pitch-based)      │    │
│     │ Chroma     │ Harmonic content (12 pitch classes)│    │
│     │ HPSS       │ Harmonic/Percussive separation     │    │
│     │ Self-Sim   │ Self-similarity matrix             │    │
│     │ MFCC       │ Mel-frequency cepstral coefficients│    │
│     │ Tempogram  │ Tempo/beat analysis                │    │
│     │ Loudness   │ Dynamic range analysis             │    │
│     └────────────┴────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Output Generation                                       │
│     - PNG/JPG format                                        │
│     - Configurable size and resolution                      │
│     - Color palette selection                               │
└─────────────────────────────────────────────────────────────┘
```

## Quick start
- Spectrogram: `songsee track.mp3`
- Multi-panel: `songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux`
- Time slice: `songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg`
- Stdin: `cat track.mp3 | songsee - --format png -o out.png`

## Common flags
| Flag | Description | Example |
|------|-------------|---------|
| `--viz` | Visualization type(s) | `--viz spectrogram,mel` |
| `--style` | Color palette | `--style magma` |
| `--width` | Output width (px) | `--width 1920` |
| `--height` | Output height (px) | `--height 1080` |
| `--window` | FFT window size | `--window 2048` |
| `--hop` | FFT hop size | `--hop 512` |
| `--min-freq` | Minimum frequency (Hz) | `--min-freq 0` |
| `--max-freq` | Maximum frequency (Hz) | `--max-freq 16000` |
| `--start` | Start time (seconds) | `--start 30` |
| `--duration` | Duration (seconds) | `--duration 10` |
| `--format` | Output format | `--format png` |

## Examples

### Basic Spectrogram
```bash
# Generate basic spectrogram
songsee track.mp3

# Save to file
songsee track.mp3 -o spectrogram.png

# Custom size
songsee track.mp3 --width 1920 --height 1080 -o hd_spectrogram.png
```

### Multi-Panel Analysis
```bash
# Generate full feature panel
songsee track.mp3 \
  --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux \
  -o full_analysis.png

# Compact panel (3 panels)
songsee track.mp3 --viz spectrogram,mel,chroma -o compact.png

# Single feature focus
songsee track.mp3 --viz chroma -o chroma.png
```

### Time-Slice Extraction
```bash
# Extract 10-second slice from 30s mark
songsee track.mp3 --start 30 --duration 10 -o slice.png

# Chorus/hook extraction
songsee track.mp3 --start 45 --duration 8 -o chorus.png

# Beat drop section
songsee track.mp3 --start 120 --duration 15 -o drop.png
```

### Style Variations
```bash
# Classic grayscale
songsee track.mp3 --style classic -o classic.png

# Fire palette
songsee track.mp3 --style inferno -o inferno.png

# Rainbow spectrum
songsee track.mp3 --style viridis -o viridis.png

# Dark mode friendly
songsee track.mp3 --style magma -o magma.png
```

### Advanced Analysis
```bash
# High frequency resolution (narrow bins)
songsee track.mp3 --window 4096 --hop 256 -o high_res.png

# Wide frequency range
songsee track.mp3 --min-freq 0 --max-freq 22050 -o full_range.png

# Bass-focused
songsee track.mp3 --min-freq 0 --max-freq 500 -o bass.png

# Treble/vocal focused
songsee track.mp3 --min-freq 2000 --max-freq 8000 -o treble.png
```

### Pipeline Integration
```bash
# Stdin input (streaming audio)
cat track.mp3 | songsee - -o output.png

# Stdout output (for further processing)
songsee track.mp3 --format png | base64 > image.txt

# Chain with ffmpeg
ffmpeg -i video.mp4 -vn -f mp3 - | songsee - --viz spectrogram -o video_spectrogram.png

# Batch process multiple tracks
for track in *.mp3; do
  songsee "$track" -o "spectrograms/${track%.mp3}.png"
done
```

### Feature Comparison
```bash
# Compare two tracks side by side
songsee track1.mp3 -o t1.png
songsee track2.mp3 -o t2.png

# Create comparison grid
montage t1.png t2.png -tile 2x1 -geometry +5+5 comparison.png

# Before/after processing comparison
sox original.wav processed.wav
songsee original.wav -o before.png
songsee processed.wav -o after.png
```

### Stacked Analysis
```bash
# Create stacked visualization
songsee track.mp3 --viz spectrogram -o layer1.png
songsee track.mp3 --viz chroma -o layer2.png
songsee track.mp3 --viz tempogram -o layer3.png

# Combine in image editor or with ImageMagick
montage layer1.png layer2.png layer3.png -tile 1x3 -geometry +0+0 stacked.png
```

### Integration with Scripts
```bash
#!/bin/bash
# Analyze and tag audio library
for f in *.mp3; do
  echo "Analyzing: $f"
  songsee "$f" --viz spectrogram,mel,tempogram \
    --width 1200 --height 800 \
    -o "analysis/${f%.mp3}_analysis.png"
done
```

```python
#!/usr/bin/env python3
import subprocess
import os

# Batch analyze with Python
tracks = [f for f in os.listdir('.') if f.endswith('.mp3')]

for track in tracks:
    output = f"analysis/{track.replace('.mp3', '.png')}"
    result = subprocess.run(
        ['songsee', track, '--viz', 'spectrogram,mel,chroma', '-o', output],
        capture_output=True,
        text=True
    )
    print(f"{track}: {'OK' if result.returncode == 0 else 'FAILED'}")
```

### Visualizations Reference

| Visualization | Description | Use Case |
|---------------|-------------|----------|
| `spectrogram` | Standard STFT | General frequency analysis |
| `mel` | Mel-spectrogram | Perceptual pitch representation |
| `chroma` | Chromagram | Harmonic content, key detection |
| `hpss` | Harmonic/Percussive | Separate melody/rhythm |
| `selfsim` | Self-similarity | Pattern detection, structure |
| `mfcc` | MFCC | Timbre, genre classification |
| `tempogram` | Tempogram | Tempo, beat tracking |
| `loudness` | Loudness envelope | Dynamics, drops |
| `flux` | Spectral flux | Change detection |

### Color Palettes

| Palette | Characteristics |
|---------|-----------------|
| `classic` | Grayscale, scientific |
| `magma` | Dark to bright orange |
| `inferno` | Black to yellow to purple |
| `viridis` | Blue to green to yellow |
| `gray` | Grayscale alternative |

## Troubleshooting

### No Output Generated
```bash
# Check file exists and is readable
ls -la track.mp3
file track.mp3

# Check ffmpeg is installed (for non-native formats)
ffmpeg -version

# Run with verbose output
songsee track.mp3 -o out.png --verbose
```

### Poor Quality Output
```bash
# Increase output dimensions
songsee track.mp3 --width 1920 --height 1080 -o hd.png

# Increase FFT window for better frequency resolution
songsee track.mp3 --window 4096 -o high_res.png

# Try different style
songsee track.mp3 --style inferno -o better_contrast.png
```

### Slow Processing
```bash
# Reduce output size
songsee track.mp3 --width 800 --height 600 -o small.png

# Shorter duration
songsee track.mp3 --duration 5 -o quick.png

# Smaller FFT window
songsee track.mp3 --window 512 --hop 128 -o fast.png

# Skip visualizations you don't need
songsee track.mp3 --viz spectrogram -o fast.png
```

### Memory Issues with Long Tracks
```bash
# Process only relevant section
songsee long_track.mp3 --start 0 --duration 60 -o section.png

# Lower resolution
songsee long_track.mp3 --width 640 --height 360 -o low_mem.png

# Use HPSS for separation
songsee long_track.mp3 --viz hpss -o hpss.png
```

### Format Conversion
```bash
# Convert non-native formats first with ffmpeg
ffmpeg -i audio.flac -write-id3v2 track.mp3
songsee track.mp3 -o out.png

# Direct ffmpeg pipe
ffmpeg -i audio.aiff -f mp3 - | songsee - -o out.png
```

### Stdin/Stdout Issues
```bash
# Verify stdin works
cat track.mp3 | songsee - -o out.png

# Check pipe integrity
cat track.mp3 | wc -c  # Should match file size

# Try explicit format
cat track.mp3 | songsee - --format png -o -
```

## Notes

- WAV/MP3 decode native; other formats use ffmpeg if available
- Multiple `--viz` renders a grid
- Default output: PNG format
- Color palettes: classic, magma, inferno, viridis, gray
