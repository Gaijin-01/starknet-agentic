---
name: sonoscli
description: Control Sonos speakers (discover/status/play/volume/group).
homepage: https://sonoscli.sh
metadata:
  {
    "openclaw":
      {
        "emoji": "🔊",
        "requires": { "bins": ["sonos"] },
        "install":
          [
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/steipete/sonoscli/cmd/sonos@latest",
              "bins": ["sonos"],
              "label": "Install sonoscli (go)",
            },
          ],
      },
  }
---

# Sonos CLI

## Overview

Control Sonos speakers on the local network via CLI. Manage playback, volume, groups, favorites, and queues for multi-room audio systems.

**When to use:**
- Controlling Sonos speakers programmatically
- Multi-room audio group management
- Playing favorites or queues
- Volume automation across zones
- Home automation integration
- Quick playback controls without the app

**Key capabilities:**
- Device discovery
- Playback control (play, pause, stop, skip)
- Volume control per speaker
- Group management (join/leave)
- Favorites management
- Queue control
- Spotify search via SMAPI

## Workflow

```
1. Discover speakers on network
2. Identify target speaker by name
3. Execute playback/volume/group command
4. Verify action completed
5. Manage groups for multi-room audio as needed
```

## Examples

**Discover speakers:**
```bash
sonos discover
```

**Check speaker status:**
```bash
sonos status --name "Kitchen"
```

**Play music:**
```bash
sonos play --name "Living Room"
```

**Pause playback:**
```bash
sonos pause --name "Bedroom"
```

**Set volume to 25%:**
```bash
sonos volume set 25 --name "Office"
```

**Group speakers for party mode:**
```bash
sonos group party "Living Room" "Kitchen" "Bedroom"
```

**Solo one speaker (mute others in group):**
```bash
sonos group solo "Kitchen"
```

**List favorites:**
```bash
sonos favorites list
```

**Play a favorite:**
```bash
sonos favorites open "My Playlist"
```

Quick start

- `sonos discover`
- `sonos status --name "Kitchen"`
- `sonos play|pause|stop --name "Kitchen"`
- `sonos volume set 15 --name "Kitchen"`

Common tasks

- Grouping: `sonos group status|join|unjoin|party|solo`
- Favorites: `sonos favorites list|open`
- Queue: `sonos queue list|play|clear`
- Spotify search (via SMAPI): `sonos smapi search --service "Spotify" --category tracks "query"`

Notes

- If SSDP fails, specify `--ip <speaker-ip>`.
- Spotify Web API search is optional and requires `SPOTIFY_CLIENT_ID/SECRET`.
