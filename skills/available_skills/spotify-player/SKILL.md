---
name: spotify-player
description: Terminal Spotify playback/search via spogo (preferred) or spotify_player.
homepage: https://www.spotify.com
metadata:
  {
    "openclaw":
      {
        "emoji": "🎵",
        "requires": { "anyBins": ["spogo", "spotify_player"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "spogo",
              "tap": "steipete/tap",
              "bins": ["spogo"],
              "label": "Install spogo (brew)",
            },
            {
              "id": "brew",
              "kind": "brew",
              "formula": "spotify_player",
              "bins": ["spotify_player"],
              "label": "Install spotify_player (brew)",
            },
          ],
      },
  }
---

# spogo / spotify_player

## Overview

Control Spotify playback and search from the terminal. Use `spogo` (preferred) or `spotify_player` as fallback. Requires Spotify Premium.

**When to use:**
- Controlling Spotify playback from CLI
- Searching for tracks, albums, artists
- Managing devices (Spotify Connect)
- Getting current playback status
- Integrating with other tools

**Key capabilities:**
- Playback control (play, pause, next, previous)
- Search tracks, albums, artists
- Device management
- Like/favorite tracks
- Current status display

## Workflow

```
1. Authenticate with Spotify (import browser cookies)
2. Choose player (spogo preferred, spotify_player fallback)
3. Execute playback or search command
4. Verify action completed
5. Manage devices if needed
```

## Examples

**Import Spotify cookies from browser:**
```bash
spogo auth import --browser chrome
```

**Search for a track:**
```bash
spogo search track "bohemian rhapsody"
```

**Playback controls:**
```bash
spogo play
spogo pause
spogo next
spogo prev
```

**List available devices:**
```bash
spogo device list
```

**Switch to specific device:**
```bash
spogo device set "Living Room"
```

**Get current playback status:**
```bash
spogo status
```

**spotify_player fallback - search:**
```bash
spotify_player search "query"
```

**spotify_player - like current track:**
```bash
spotify_player like
```

Requirements

- Spotify Premium account.
- Either `spogo` or `spotify_player` installed.

spogo setup

- Import cookies: `spogo auth import --browser chrome`

Common CLI commands

- Search: `spogo search track "query"`
- Playback: `spogo play|pause|next|prev`
- Devices: `spogo device list`, `spogo device set "<name|id>"`
- Status: `spogo status`

spotify_player commands (fallback)

- Search: `spotify_player search "query"`
- Playback: `spotify_player playback play|pause|next|previous`
- Connect device: `spotify_player connect`
- Like track: `spotify_player like`

Notes

- Config folder: `~/.config/spotify-player` (e.g., `app.toml`).
- For Spotify Connect integration, set a user `client_id` in config.
- TUI shortcuts are available via `?` in the app.
