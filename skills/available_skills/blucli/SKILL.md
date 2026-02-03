---
name: blucli
description: BluOS CLI (blu) for discovery, playback, grouping, and volume.
homepage: https://blucli.sh
metadata:
  {
    "openclaw":
      {
        "emoji": "🫐",
        "requires": { "bins": ["blu"] },
        "install":
          [
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/steipete/blucli/cmd/blu@latest",
              "bins": ["blu"],
              "label": "Install blucli (go)",
            },
          ],
      },
  }
---

# blucli (blu)

## Overview

Control Bluesound and NAD audio players that use the BluOS ecosystem. Discover devices on the network, control playback, manage groups for multi-room audio, and adjust volume programmatically.

**When to use:**
- Controlling multi-room audio systems
- Managing speaker groups
- Playing/pausing music across devices
- Volume control automation
- Integration with other home automation tools
- Scripting audio playback for events or routines

**Key capabilities:**
- Device discovery on local network
- Playback control (play, pause, stop, next, previous)
- Volume adjustment per device
- Group management (join/leave groups)
- TuneIn radio search and playback
- Status monitoring

## Workflow

```
1. Discover available devices on the network
2. Identify target device by name, ID, or alias
3. Execute playback or volume command
4. Verify action completed successfully
5. Group/ungroup devices as needed for multi-room audio
```

## Examples

**List all devices:**
```bash
blu devices
```

**Check status of specific device:**
```bash
blu --device "Living Room" status
```

**Play music:**
```bash
blu --device "Kitchen" play
```

**Pause playback:**
```bash
blu --device "Office" pause
```

**Set volume to 30%:**
```bash
blu --device "Bedroom" volume set 30
```

**Group devices for multi-room audio:**
```bash
blu group add "Living Room" "Kitchen"
```

**Search and play TuneIn radio:**
```bash
blu tunein search "BBC Radio 1"
blu tunein play "BBC Radio 1"
```

**Using environment variable for default device:**
```bash
export BLU_DEVICE="Living Room"
blu status
blu play
```

Quick start

- `blu devices` (pick target)
- `blu --device <id> status`
- `blu play|pause|stop`
- `blu volume set 15`

Target selection (in priority order)

- `--device <id|name|alias>`
- `BLU_DEVICE`
- config default (if set)

Common tasks

- Grouping: `blu group status|add|remove`
- TuneIn search/play: `blu tunein search "query"`, `blu tunein play "query"`

Prefer `--json` for scripts. Confirm the target device before changing playback.
