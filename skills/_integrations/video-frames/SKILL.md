---
name: video-frames
description: Extract frames or short clips from videos using ffmpeg.
homepage: https://ffmpeg.org
metadata:
  {
    "openclaw":
      {
        "emoji": "🎞️",
        "requires": { "bins": ["ffmpeg"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install ffmpeg (brew)",
            },
          ],
      },
  }
---

# Video Frames (ffmpeg)

## Overview

Extract individual frames from video files as images using ffmpeg. Create thumbnails, keyframes, or time-slice captures for inspection and analysis.

**When to use:**
- Creating thumbnails from videos
- Extracting key frames for analysis
- Generating preview images
- Frame-by-frame video inspection
- Creating image sequences from video
- Quick visual inspection of video content

**Key capabilities:**
- Single frame extraction
- Timestamp-based extraction
- Multiple output formats (jpg, png)
- Quality control
- Sequence extraction

## Workflow

```
1. Identify video file and extraction goal
2. Choose extraction method (single, interval, timestamp)
3. Run extraction command
4. Verify output images
```

## Examples

**Extract first frame:**
```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
```

**Extract frame at timestamp (10 seconds):**
```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

**Extract frame at 50% of video:**
```bash
ffmpeg -i video.mp4 -ss $(ffprobe -i video.mp4 -format_format none -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 | awk '{printf "%.0f", $1 * 0.5}') -vframes 1 middle.jpg
```

**Extract every 60 seconds as sequence:**
```bash
ffmpeg -i video.mp4 -vf "fps=1/60" frame_%04d.jpg
```

**Create thumbnail with specific size:**
```bash
ffmpeg -i video.mp4 -ss 00:00:05 -vframes 1 -vf "scale=320:-1" thumbnail.jpg
```

**Extract high-quality PNG frame:**
```bash
ffmpeg -i video.mp4 -ss 00:00:03 -vframes 1 -q:v 2 frame.png
```

## Quick start

First frame:

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --out /tmp/frame.jpg
```

At a timestamp:

```bash
{baseDir}/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

## Notes

- Prefer `--time` for “what is happening around here?”.
- Use a `.jpg` for quick share; use `.png` for crisp UI frames.
