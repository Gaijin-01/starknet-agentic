---
name: camsnap
description: Capture frames or clips from RTSP/ONVIF cameras.
homepage: https://camsnap.ai
metadata: {"clawdbot":{"emoji":"📸","requires":{"bins":["camsnap"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/camsnap","bins":["camsnap"],"label":"Install camsnap (brew)"}]}}
---

# camsnap

## Overview

Use `camsnap` to grab snapshots, clips, or motion events from configured RTSP/ONVIF cameras. This skill provides programmatic access to camera feeds for security monitoring, time-lapse capture, and motion detection.

**Key Capabilities:**
- Capture single frames (snapshots)
- Record video clips of specified duration
- Monitor motion events with configurable thresholds
- Camera discovery and health diagnostics
- Support for RTSP and ONVIF protocols

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Camsnap Workflow                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Configure Cameras                                       │
│     - Edit ~/.config/camsnap/config.yaml                    │
│     - Add cameras with host, credentials                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Discover & Test                                         │
│     - camsnap discover --info                                │
│     - camsnap doctor --probe                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Capture Mode                                            │
│     ┌─────────────┬─────────────┬─────────────┐             │
│     │   Snapshot  │    Clip     │    Watch    │             │
│     │  (single)   │  (duration) │  (motion)   │             │
│     └─────────────┴─────────────┴─────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## Setup
- Config file: `~/.config/camsnap/config.yaml`
- Add camera: `camsnap add --name kitchen --host 192.168.0.10 --user user --pass pass`

Common commands
- Discover: `camsnap discover --info`
- Snapshot: `camsnap snap kitchen --out shot.jpg`
- Clip: `camsnap clip kitchen --dur 5s --out clip.mp4`
- Motion watch: `camsnap watch kitchen --threshold 0.2 --action '...'`
- Doctor: `camsnap doctor --probe`

Notes
- Requires `ffmpeg` on PATH.
- Prefer a short test capture before longer clips.

## Examples

### Basic Snapshot Capture
```bash
# Capture a single frame from living-room camera
camsnap snap living-room --out /tmp/snapshot.jpg

# Capture with custom resolution
camsnap snap front-door --out door.jpg --width 1920 --height 1080
```

### Video Clip Recording
```bash
# Record 10-second clip
camsnap clip living-room --dur 10s --out clip.mp4

# Record 30-second clip at lower quality for bandwidth
camsnap clip garage --dur 30s --out garage.mp4 --quality medium
```

### Motion Detection Setup
```bash
# Watch for motion with default threshold (0.2)
camsnap watch living-room --action 'echo Motion detected!'

# Watch with custom threshold (higher = less sensitive)
camsnap watch front-door --threshold 0.4 --action 'notify-send "Door motion!"'

# Watch with output to file on motion
camsnap watch driveway --threshold 0.3 --out /tmp/motion_$(date +%s).jpg
```

### Camera Discovery & Diagnostics
```bash
# Discover all cameras on network
camsnap discover --info

# Run diagnostics on configured cameras
camsnap doctor --probe
camsnap doctor --probe --camera living-room
```

### Integration with Home Automation
```bash
# Trigger via cron for regular snapshots
# 0 * * * * camsnap snap porch --out /var/www/porch.jpg

# Motion trigger script
#!/bin/bash
camsnap watch doorbell --threshold 0.3 --action 'curl -X POST http://homeassistant:8123/api/webhook/doorbell_motion'
```

### Batch Operations
```bash
# Capture from all cameras
for cam in living-room front-door garage; do
  camsnap snap $cam --out /snapshots/$cam_$(date +%Y%m%d_%H%M%S).jpg
done
```

## Troubleshooting

### Connection Failed
```bash
# Check camera is reachable
ping 192.168.0.10

# Verify RTSP port
nc -zv 192.168.0.10 554

# Test with camsnap doctor
camsnap doctor --probe --camera kitchen
```

### No Video / Black Frames
```bash
# Verify ffmpeg is installed
ffmpeg -version

# Check camera credentials
camsnap doctor --camera kitchen

# Try manual snapshot with verbose output
camsnap snap kitchen --out test.jpg --verbose
```

### Motion Detection Not Triggering
```bash
# Lower the threshold (0.1 = very sensitive)
camsnap watch living-room --threshold 0.1 --action 'echo Motion!'

# Check lighting conditions
# Motion detection requires visible changes in frame
```

### Performance Issues
```bash
# Reduce resolution for bandwidth
camsnap snap cam --width 1280 --height 720

# Use shorter clips
camsnap clip cam --dur 5s

# Check camera FPS settings
# Lower FPS = less bandwidth, slower detection
```
