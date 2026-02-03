---
name: openhue
description: Control Philips Hue lights/scenes via the OpenHue CLI.
homepage: https://www.openhue.io/cli
metadata:
  {
    "openclaw":
      {
        "emoji": "💡",
        "requires": { "bins": ["openhue"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "openhue/cli/openhue-cli",
              "bins": ["openhue"],
              "label": "Install OpenHue CLI (brew)",
            },
          ],
      },
  }
---

# OpenHue CLI

## Overview

Control Philips Hue lights, rooms, and scenes via CLI. Manage home lighting programmatically through the Hue Bridge.

**When to use:**
- Controlling lights on/off and brightness
- Setting light colors via RGB
- Activating scenes
- Managing rooms of lights
- Home automation integration
- Lighting routines and schedules

**Key capabilities:**
- Light control (on/off, brightness, color)
- Room management
- Scene activation
- Bridge discovery and setup
- JSON output for automation

## Workflow

```
1. Set up OpenHue with Hue Bridge (press button during setup)
2. Discover lights, rooms, and scenes
3. Identify target by ID or name
4. Execute control command
5. Verify changes
```

## Examples

**Discover bridges on network:**
```bash
openhue discover
```

**Guided setup:**
```bash
openhue setup
```

**List all lights (JSON):**
```bash
openhue get light --json
```

**List rooms:**
```bash
openhue get room --json
```

**List scenes:**
```bash
openhue get scene --json
```

**Turn on a light:**
```bash
openhue set light "Living Room" --on
```

**Turn off a light:**
```bash
openhue set light 5 --off
```

**Set brightness to 50%:**
```bash
openhue set light 5 --on --brightness 50
```

**Set light color:**
```bash
openhue set light 5 --on --rgb #3399FF
```

**Activate a scene:**
```bash
openhue set scene "Relax"
```

Setup

- Discover bridges: `openhue discover`
- Guided setup: `openhue setup`

Read

- `openhue get light --json`
- `openhue get room --json`
- `openhue get scene --json`

Write

- Turn on: `openhue set light <id-or-name> --on`
- Turn off: `openhue set light <id-or-name> --off`
- Brightness: `openhue set light <id> --on --brightness 50`
- Color: `openhue set light <id> --on --rgb #3399FF`
- Scene: `openhue set scene <scene-id>`

Notes

- You may need to press the Hue Bridge button during setup.
- Use `--room "Room Name"` when light names are ambiguous.
